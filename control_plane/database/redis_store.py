import redis
import json
import os
import logging

logger = logging.getLogger("RedisStore")

# Simple atomic LUA script to book a node. 
# It checks if node is ONLINE and has enough VRAM. If yes, it deducts VRAM and returns 1.
# This prevents race conditions when 10 000 RPS hit the scheduler.
RESERVE_NODE_LUA = """
local node_key = KEYS[1]
local required_vram = tonumber(ARGV[1])

local current_status = redis.call('HGET', node_key, 'status')
if current_status ~= 'ONLINE' and current_status ~= 'SUPERPOSITION' then
    return -1 -- Not routable
end

local available_vram = tonumber(redis.call('HGET', node_key, 'vram_free') or '0')
if available_vram >= required_vram then
    redis.call('HSET', node_key, 'vram_free', available_vram - required_vram)
    return 1 -- OK Booked
else
    return 0 -- Insufficient VRAM
end
"""

# Phase 4.4: Virtual Credit Engine LUA Script
# Atomically decrements the buyer's credit balance and increments the node's unsettled ledger
DECREMENT_CREDITS_LUA = """
local dev_key = KEYS[1]
local node_key = KEYS[2]
local credit_cost = tonumber(ARGV[1])
local avr_reward = tonumber(ARGV[2])

local current_credits = tonumber(redis.call('GET', dev_key) or '0')
if current_credits >= credit_cost then
    redis.call('DECRBY', dev_key, credit_cost)
    redis.call('HINCRBYFLOAT', node_key, 'earned_avr', avr_reward)
    return 1 -- TX Success
else
    return 0 -- Insufficient Funds
end
"""

class RedisStateGrid:
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            redis_url = os.environ.get("REDIS_URL")
            if redis_url:
                self.client = redis.from_url(redis_url, decode_responses=True)
            else:
                self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.reserve_script = self.client.register_script(RESERVE_NODE_LUA)
            self.settle_script = self.client.register_script(DECREMENT_CREDITS_LUA)
            logger.info(f"Connected to Redis In-Memory Grid at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    def update_node_state(self, node_id: str, state: dict):
        """Called by the NATS Aggregator to update the <10ms state grid"""
        if not self.client: return
        key = f"node:{node_id}"
        self.client.hset(key, mapping=state)
        # Keep ephemeral states fleeting. If a node drops, it disappears in 5 seconds.
        self.client.expire(key, 5)

    def reserve_node_capacity(self, node_id: str, required_vram_gb: int) -> bool:
        """Atomically checks and reserves VRAM on a node. Solves Double-Booking."""
        if not self.client: return False
        key = f"node:{node_id}"
        result = self.reserve_script(keys=[key], args=[required_vram_gb])
        return result == 1
        
    def get_all_routable_nodes(self):
        """Fetches all keys quickly. In production, we'd use Redis Search (RediSearch) for Geo-Spatial & numeric filtering."""
        if not self.client: return []
        keys = self.client.keys("node:*")
        nodes = []
        for k in keys:
            data = self.client.hgetall(k)
            if data and data.get("status") in ["ONLINE", "SUPERPOSITION"]:
                data["id"] = k.replace("node:", "")
                nodes.append(data)
        return nodes
        
    def settle_invoice(self, developer_id: str, node_id: str, tokens: int) -> bool:
        """Phase 4.4: Executes a sub-millisecond microtransaction between Dev and Node"""
        if not self.client: return False
        dev_key = f"dev:{developer_id}:credits"
        node_key = f"node:{node_id}"
        
        # 1 token = 1 credit = 0.000001 AVR
        credit_cost = tokens
        avr_reward = float(tokens) * 0.000001
        
        result = self.settle_script(keys=[dev_key, node_key], args=[credit_cost, avr_reward])
        return result == 1

redis_store = RedisStateGrid()

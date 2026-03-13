import time
import uuid
import random
import threading
import logging
import os

try:
    import redis
except ImportError:
    pass

logger = logging.getLogger("MockEngine")
logger.setLevel(logging.INFO)

class MockDataEngine:
    """Injects 200+ fake nodes into Redis to simulate a living global network for the Dashboard presentation."""
    def __init__(self, host='localhost', port=6379):
        self.running = False
        try:
            redis_url = os.environ.get("REDIS_URL")
            if redis_url:
                self.client = redis.from_url(redis_url, decode_responses=True)
            else:
                self.client = redis.Redis(host=host, port=port, db=0, decode_responses=True)
        except Exception:
            self.client = None
            
        self.mock_nodes = []
        self._init_mock_nodes()

    def _init_mock_nodes(self):
        locations = ["us-east-1", "eu-central-1", "ap-northeast-1", "sa-east-1", "us-west-2", "eu-north-1"]
        for _ in range(250): # 250 fake nodes
            node_id = str(uuid.uuid4())
            self.mock_nodes.append({
                "id": node_id,
                "location": random.choice(locations),
                "base_vram": random.choice([24, 48, 80]),
                "base_temp": random.randint(35, 55),
                "base_ping": random.randint(5, 120),
                "earned_avr": random.uniform(5.0, 5000.0)
            })

    def start(self):
        if not self.running and self.client:
            self.running = True
            threading.Thread(target=self._run_loop, daemon=True).start()
            logger.info("Mock Data Engine Started: Injecting 250 virtual nodes into Redis.")

    def stop(self):
        self.running = False

    def _run_loop(self):
        while self.running:
            try:
                pipeline = self.client.pipeline()
                for node in self.mock_nodes:
                    # Randomly fluctuate metrics
                    vram_fluctuation = random.uniform(-2.0, 2.0)
                    temp_fluctuation = random.uniform(-1.0, 3.0)
                    ping_fluctuation = random.uniform(-5.0, 5.0)
                    
                    # 5% chance a node enters SUPERPOSITION update state
                    status = "ONLINE"
                    if random.random() < 0.05:
                        status = "SUPERPOSITION"
                        
                    # Earn trickle income
                    node["earned_avr"] += random.uniform(0.0001, 0.005)
                    
                    data = {
                        "status": status,
                        "vram_free": str(max(0, node["base_vram"] + vram_fluctuation)),
                        "temperature_c": str(max(20, node["base_temp"] + temp_fluctuation)),
                        "ping_ms": str(max(1, node["base_ping"] + ping_fluctuation)),
                        "pcie_bw": str(random.uniform(5000, 15000)),
                        "earned_avr": str(node["earned_avr"]),
                        "location": node["location"]
                    }
                    pipeline.hset(f"node:{node['id']}", mapping=data)
                    pipeline.expire(f"node:{node['id']}", 30) # 30 sec TTL
                
                pipeline.execute()
            except Exception as e:
                logger.error(f"Mock Engine error: {e}")
                
            time.sleep(2.0) # Update mock state every 2 seconds

mock_engine = MockDataEngine()

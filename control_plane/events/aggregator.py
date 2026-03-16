import asyncio
import json
import logging
from nats.js.errors import NotFoundError
from control_plane.events.nats_client import nats_bus
from control_plane.database.redis_store import redis_store

logger = logging.getLogger("Aggregator")

class Aggregator:
    def __init__(self):
        self._task = None

    async def _process_stream(self):
        # Wait for NATS to connect properly before subscribing
        while not nats_bus.js:
            await asyncio.sleep(0.5)
            
        js = nats_bus.js

        try:
            # Subscribing to node.telemetry.> pattern
            sub = await js.subscribe("node.telemetry.>", stream="TELEMETRY")
            logger.info("Aggregator started listening to NATS Telemetry stream...")
            
            async for msg in sub.messages:
                try:
                    data = json.loads(msg.data.decode())
                    node_id = msg.subject.split(".")[-1]
                    
                    # Read available VRAM for routing
                    vram_free = data.get("vram_free", data.get("gpu_vram", 0))
                    
                    state = {
                        "status": "ONLINE",  
                        "vram_free": vram_free, 
                        "temperature_c": data.get("temperature_c", 0),
                        "pcie_bw": data.get("pcie_bw_usage", 0.0),
                        "cpu_cores": data.get("cpu_cores", 4),
                        "memory_mb": data.get("memory_mb", 16000),
                        "location": data.get("location", "local"),
                        "address": data.get("address", "unknown"),
                    }
                    
                    # Store in Redis
                    redis_store.update_node_state(node_id, state)
                    # Acknowledge the message so NATS drops it
                    await msg.ack()
                except Exception as e:
                    logger.error(f"Aggregator error processing message: {e}")
        except Exception as e:
            logger.error(f"Aggregator failed to subscribe: {e}")

    def start(self):
        loop = asyncio.get_event_loop()
        self._task = loop.create_task(self._process_stream())
        
aggregator = Aggregator()

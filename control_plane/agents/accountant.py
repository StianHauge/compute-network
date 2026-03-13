import asyncio
import logging
from datetime import datetime
from control_plane.database import schema
from control_plane.database.redis_store import redis_store

logger = logging.getLogger("TheAccountant")

class AccountantWorker:
    def __init__(self):
        self._task = None
        self.running = False

    async def _settlement_loop(self):
        logger.info("The Accountant started: Commencing asynchronous global settlement engine.")
        while self.running:
            try:
                # Settle once per hour in production. Every 60 seconds for this prototype.
                await asyncio.sleep(60) 
                self._run_settlement()
            except Exception as e:
                logger.error(f"Settlement failed: {e}")

    def _run_settlement(self):
        db = schema.SessionLocal()
        try:
            logger.info("INITIATING LEDGER SETTLEMENT: Sweeping Unsettled Redis AVR into DB.")
            
            # Find all nodes in Redis
            node_keys = redis_store.client.keys("node:*")
            settled_count = 0
            total_avr_minted = 0.0
            
            for key in node_keys:
                # We pull the un-swept balances that the LUA script generated
                earned_redis = float(redis_store.client.hget(key, "earned_avr") or 0.0)
                
                if earned_redis > 0:
                    node_id = key.split(":")[1]
                    node = db.query(schema.Node).filter(schema.Node.id == node_id).first()
                    if node:
                        # Sweep to persistent database / blockchain
                        node.earned_avr = float(node.earned_avr or 0) + earned_redis
                        
                        # Reset the Redis ledger atomically (HSET earned_avr 0)
                        redis_store.client.hset(key, "earned_avr", 0.0)
                        
                        settled_count += 1
                        total_avr_minted += earned_redis
            
            if settled_count > 0:
                db.commit()
                logger.info(f"SETTLEMENT COMPLETE: Synced {settled_count} nodes. Minted {total_avr_minted:.4f} AVR.")

        finally:
            db.close()

    def start(self):
        if not self.running:
            self.running = True
            loop = asyncio.get_event_loop()
            self._task = loop.create_task(self._settlement_loop())

    def stop(self):
        self.running = False
        
accountant = AccountantWorker()

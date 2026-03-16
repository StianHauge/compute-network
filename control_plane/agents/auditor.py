import time
import threading
import uuid
import logging
from datetime import datetime, timedelta

from control_plane.database import schema

logger = logging.getLogger("AuditorAgent")
logger.setLevel(logging.INFO)

class AuditorAgent:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _run_loop(self):
        while self.running:
            self._audit_nodes()
            time.sleep(15)  # Poll every 15 seconds

    def _audit_nodes(self):
        db = schema.SessionLocal()
        try:
            from control_plane.database.redis_store import redis_store
            
            # 1. Fetch live nodes from Redis
            live_nodes_data = redis_store.get_all_routable_nodes()
            
            # Find nodes that need auditing, prioritize SUPERPOSITION nodes
            for n_data in live_nodes_data:
                node_id = n_data["id"]
                status = n_data.get("status", "ONLINE")
                
                # Check if we already have an active audit for this node
                active_audit = db.query(schema.Job).filter(
                    schema.Job.node_id == node_id,
                    schema.Job.task_type == "audit",
                    schema.Job.status.in_([schema.JobStatus.PENDING, schema.JobStatus.RUNNING])
                ).first()
                if active_audit:
                    continue

                # We will audit a selection of nodes. 
                # If they are in SUPERPOSITION, we audit them aggressively to verify the new v1.2 container.
                if status != "SUPERPOSITION" and uuid.uuid4().hex[-1] not in ['0', '1']:
                    # Only ~12.5% chance to randomly audit stable ONLINE nodes per cycle
                    continue

                # Final check: the node MUST exist in the DB
                db_node = db.query(schema.Node).filter(schema.Node.id == node_id).first()
                if not db_node:
                    continue

                # The Honey-Pot: Deterministic Mathematical Prompt
                job_id = str(uuid.uuid4())
                prompt = "Calculate precisely: 345 * 12. Output only the final numerical answer."
                expected_answer = "4140"
                
                # Force temperature 0.0 for deterministic logprobs
                new_job = schema.Job(
                    id=job_id,
                    task_type="audit",
                    # Assume mistral-7b for now
                    model="mistral-7b", 
                    messages=[{"role": "user", "content": prompt}],
                    parameters={"max_tokens": 10, "temperature": 0.0, "expected_answer": expected_answer},
                    status=schema.JobStatus.PENDING,
                    node_id=node_id
                )
                db.add(new_job)
                db.commit()
                logger.info(f"Dispatched The Honey-Pot (Trap-Prompt) to node {node_id} (Status: {status})")

            # 2. Score completed Trap-Prompts
            unscored_audits = db.query(schema.Job).filter(
                schema.Job.task_type == "audit",
                schema.Job.status == schema.JobStatus.COMPLETED
            ).all()
            
            for job in unscored_audits:
                node = db.query(schema.Node).filter(schema.Node.id == job.node_id).first()
                if node:
                    result_text = job.result_logs or ""
                    expected = (job.parameters or {}).get("expected_answer", "")
                    
                    # Cryptographic/Deterministic validation
                    # In a real scenario we'd check the exact Logprobs of the returning tensor
                    if expected in result_text and job.ttft_ms is not None and job.ttft_ms < 3000:
                        # Success: Minor reputation bump
                        score_change = 1
                        node.reputation_score = min(100, (node.reputation_score or 100) + score_change)
                        logger.info(f"Node {node.id} PASSED Honey-Pot. Score: {node.reputation_score}")
                    else:
                        # FAILED: The node lied about processing the prompt, or returned garbage to game TTFT
                        score_change = -50 
                        node.reputation_score = max(0, (node.reputation_score or 100) + score_change)
                        logger.warning(f"🚨 SYBIL DETECTED! Node {node.id} FAILED Honey-Pot validation. Reputation SLASHED to {node.reputation_score}")
                        
                        # Phase 4.4 hook: Direct Economic Slashing
                        slash_amount = 500.0 # Burn 500 AVR
                        node.staked_avr = max(0.0, float(node.staked_avr or 0) - slash_amount)
                        logger.warning(f"💸 ECONOMIC IMPACT: Burned {slash_amount} AVR from Node {node.id} staked balance. Remaining: {node.staked_avr}")
                        
                db.delete(job)
                db.commit()
                
            # 3. Penalize stuck audits
            stuck_threshold = datetime.utcnow() - timedelta(minutes=1)
            stuck_audits = db.query(schema.Job).filter(
                schema.Job.task_type == "audit",
                schema.Job.status.in_([schema.JobStatus.PENDING, schema.JobStatus.RUNNING]),
                schema.Job.created_at < stuck_threshold
            ).all()
            
            for job in stuck_audits:
                node = db.query(schema.Node).filter(schema.Node.id == job.node_id).first()
                if node:
                    node.reputation_score = max(0, (node.reputation_score or 100) - 10)
                    logger.warning(f"Node {node.id} failed audit (timeout). Score reduced to {node.reputation_score}")
                
                db.delete(job)
                db.commit()

        except Exception as e:
            logger.error(f"Auditor encountered an error: {e}")
        finally:
            db.close()

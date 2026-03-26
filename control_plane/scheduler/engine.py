import time
import threading
from datetime import datetime, timedelta
from typing import List
import logging

from control_plane.database import schema

logger = logging.getLogger("Scheduler")
logger.setLevel(logging.INFO)

class Scheduler:
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
            self._schedule_jobs()
            time.sleep(5)  # Poll every 5 seconds

    def _schedule_jobs(self):
        db = schema.SessionLocal()
        try:
            # 1. Get all queued jobs
            pending_jobs = db.query(schema.Job).filter(schema.Job.status == schema.JobStatus.QUEUED).all()
            if not pending_jobs:
                return

            # 2. Get all live, routable nodes from Redis!
            from control_plane.database.redis_store import redis_store
            live_nodes_data = redis_store.get_all_routable_nodes()
            if not live_nodes_data:
                return
                
            online_node_ids = [n["id"] for n in live_nodes_data]

            # 3. Fetch their persistent historical data (TTFT, Models) from SQLite
            # In a true hyper-scale production environment, EVEN this would be in Redis or ScyllaDB
            online_nodes = db.query(schema.Node).filter(schema.Node.id.in_(online_node_ids)).all()
            
            # Map dynamic Redis state to the Node objects for the scheduler to use
            redis_map = {n["id"]: n for n in live_nodes_data}
            for n in online_nodes:
                state = redis_map.get(n.id, {})
                n.current_status_redis = state.get("status", "ONLINE")
                n.vram_free_redis = float(state.get("vram_free", 0) or 0)

            # 4. Try to assign jobs
            for job in pending_jobs:
                if job.node_id:
                    continue
                
                reqs = job.parameters or {}
                # Drop required VRAM to 1GB to support simulated Intel Mac Nodes taking jobs
                req_vram = reqs.get("vram_required", 1)

                # Find best node with TPL mathematics that ALREADY has the model loaded
                assigned_node = self._find_best_node(job, online_nodes, req_vram)
                if assigned_node:
                    # Phase 4.1: CAS Reservation in Redis to prevent Double-Booking!
                    if redis_store.reserve_node_capacity(assigned_node.id, req_vram):
                        logger.info(f"Assigned job {job.id} to nod e {assigned_node.id}. (Hot Start)")
                        job.node_id = assigned_node.id
                        # Signal the user via SSE that generation is starting
                        redis_store.redis.publish(f"job:{job.id}", '{"status": "Model loaded. Generating..."}')
                        db.commit()
                    else:
                         logger.warning(f"Race condition averted! Node {assigned_node.id} lost capacity.")
                else:
                    # FALLBACK: Cold Start (Model Preloading)
                    # Find any node with enough VRAM, even if it doesn't have the model loaded
                    logger.info(f"No Hot Nodes found for {job.id}. Attempting a Cold Start Preload.")
                    fallback_node = self._find_best_node(job, online_nodes, req_vram, require_model=False)
                    
                    if fallback_node:
                        if redis_store.reserve_node_capacity(fallback_node.id, req_vram):
                            logger.info(f"Assigning PRELOAD to Node {fallback_node.id}.")
                            job.node_id = fallback_node.id
                            job.status = schema.JobStatus.PRELOADING
                            # Signal the user that we are warming up the model
                            redis_store.redis.publish(f"job:{job.id}", f'{{"status": "Cold start: Preloading model {job.model} to Node {fallback_node.id}..."}}')
                            db.commit()
                            
                            # In reality, you'd send a NATS message to `node.{id}.preload` here.
                            # For now, the Node Agent will pick up PRELOADING jobs from its poll.
                        else:
                            logger.warning(f"Fallback Node {fallback_node.id} lost capacity.")
                    else:
                        logger.warning(f"Network Out of Capacity for job {job.id}. AWAITING_CAPACITY.")
                        job.status = schema.JobStatus.AWAITING_CAPACITY
                        redis_store.redis.publish(f"job:{job.id}", '{"status": "Awaiting network capacity..."}')
                        db.commit()

        finally:
            db.close()

    def _find_best_node(self, job: schema.Job, nodes: List[schema.Node], req_vram: int, require_model: bool = True) -> schema.Node:
        reqs = job.parameters or {}
        req_tp = reqs.get("tensor_parallel_size", 1)
        req_quant = reqs.get("quantization", "fp16")
        target_model = job.model
        
        capable_nodes = []
        for n in nodes:
            # Phase 4.1: Check dynamic VRAM from Redis, not static SQLite!
            if getattr(n, "vram_free_redis", 0) < req_vram:
                continue
                
            if (n.gpu_count or 1) < req_tp:
                continue
                
            if require_model:
                has_model = False
                for mc in n.cached_models:
                    if mc.model_name == target_model and mc.quantization == req_quant:
                        if mc.tensor_parallel_size >= req_tp:
                            has_model = True
                            break
                            
                if not has_model:
                    continue
                
            capable_nodes.append(n)
                
        if not capable_nodes:
            # Removed redundant logging here since the loop handles fallback info
            return None
            
        # The TPL (Total Perceived Latency) Formula
        # TPL = L_net + (TTFT_base * (1 + P_q)) + J_ema - S_bonus
        def calculate_tpl(node):
            # 1. L_net (Mocking GeoIP ping for now, assuming 20ms baseline)
            l_net = 20.0 
            
            # 2. TTFT_base
            ttft_base = node.avg_ttft_ms if node.avg_ttft_ms > 0 else 5000.0 # Punish unknown nodes
            
            # 3. P_q (Superposition Penalty)
            p_q = 0.15 if getattr(node, "current_status_redis", "ONLINE") == "SUPERPOSITION" else 0.0
            
            # 4. J_ema (Jitter / Stability penalty)
            j_ema = (100 - (node.reputation_score or 100)) * 5.0 # Max 500ms penalty for bad rep
            
            # 5. Phase 4.4: S_bonus (Staking Bonus)
            # Reduce perceived latency effectively "boosting" the node up the queue if they stake AVR.
            # Max 100ms boost for 100k AVR staked.
            s_bonus = min(100.0, (float(node.staked_avr or 0) / 100000.0) * 100.0)
            
            tpl = l_net + (ttft_base * (1.0 + p_q)) + j_ema - s_bonus
            
            # Phase 4.4: Tiered Priority filtering (Enterprise Queue)
            if reqs.get("priority") == "tiered":
                if float(node.staked_avr or 0) < 50000.0:
                    tpl += 999999.0 # Effectively banish them from this queue
            
            # Internal node fallback penalty
            if node.node_type == schema.NodeType.INTERNAL:
                tpl += 1000000.0  
                
            return tpl
            
        capable_nodes.sort(key=calculate_tpl)
        return capable_nodes[0]

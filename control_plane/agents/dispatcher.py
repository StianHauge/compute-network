import time
import threading
import uuid
import logging
from datetime import datetime, timedelta

from control_plane.database import schema

logger = logging.getLogger("DispatcherAgent")
logger.setLevel(logging.INFO)

class DispatcherAgent:
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
        # Initial sleep to let network settle
        time.sleep(10)
        while self.running:
            self._optimize_network()
            time.sleep(10)

    def _optimize_network(self):
        db = schema.SessionLocal()
        try:
            # 1. Analyze recent traffic (last 5 minutes)
            recent_time = datetime.utcnow() - timedelta(minutes=5)
            
            recent_jobs = db.query(schema.Job).filter(
                schema.Job.task_type == "llm_inference",
                schema.Job.created_at >= recent_time
            ).all()
            
            if not recent_jobs:
                return
                
            demand = {}
            for j in recent_jobs:
                demand[j.model] = demand.get(j.model, 0) + 1
                
            sorted_demand = sorted(demand.items(), key=lambda x: x[1], reverse=True)
            top_model = sorted_demand[0][0]
            
            # 2. Check current supply
            online_nodes = db.query(schema.Node).filter(schema.Node.status == schema.NodeStatus.ONLINE).all()
            supply_count = 0
            eligible_idle_nodes = []
            
            for node in online_nodes:
                has_model = any(mc.model_name == top_model for mc in node.cached_models)
                if has_model:
                    supply_count += 1
                else:
                    active_jobs = [j for j in node.jobs if j.status in [schema.JobStatus.PENDING, schema.JobStatus.RUNNING]]
                    if not active_jobs:
                        eligible_idle_nodes.append(node)
                        
            # logger.info(f"Market Analysis - Demand for '{top_model}': {demand[top_model]} reqs. Supply: {supply_count} nodes.")
            
            # 3. Scale up if supply is low
            if demand[top_model] > supply_count and eligible_idle_nodes:
                target_node = eligible_idle_nodes[0]
                job_id = str(uuid.uuid4())
                
                logger.info(f"Dispatcher triggering scale-up: Ordering Node {target_node.id[:8]} to preload {top_model}")
                
                new_job = schema.Job(
                    id=job_id,
                    task_type="preload_model",
                    model=top_model,
                    status=schema.JobStatus.PENDING,
                    node_id=target_node.id
                )
                db.add(new_job)
                db.commit()

        except Exception as e:
            logger.error(f"Dispatcher encountered an error: {e}")
        finally:
            db.close()

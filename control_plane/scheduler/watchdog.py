import time
import threading
from datetime import datetime, timedelta
import logging

from control_plane.database import schema
from control_plane.database.redis_store import redis_store

logger = logging.getLogger("Watchdog")
logger.setLevel(logging.INFO)

class WatchdogAgent:
    def __init__(self):
        self.running = False
        self.thread = None
        # How long a job can remain PRELOADING before we consider the node dead
        self.PRELOAD_TIMEOUT_SECONDS = 15 * 60  # 15 minutes
        # How long a job can remain RUNNING without an updated chunk timestamp
        self.RUNNING_TIMEOUT_SECONDS = 30  # 30 seconds

    def start(self):
        if not self.running:
            self.running = True
            logger.info("Watchdog Service Started: Monitoring active jobs for fault tolerance.")
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _run_loop(self):
        while self.running:
            self._scan_for_stalled_jobs()
            time.sleep(10)  # Sweep the database every 10 seconds

    def _scan_for_stalled_jobs(self):
        db = schema.SessionLocal()
        try:
            now = datetime.utcnow()
            
            # 1. Recover Jobs stuck in PRELOADING
            preload_timeout_threshold = now - timedelta(seconds=self.PRELOAD_TIMEOUT_SECONDS)
            stalled_preloading = db.query(schema.Job).filter(
                schema.Job.status == schema.JobStatus.PRELOADING,
                schema.Job.created_at < preload_timeout_threshold
            ).all()

            for job in stalled_preloading:
                self._handle_stalled_job(db, job, "PRELOADING timeout (Cold Start Failed)")

            # 2. Recover Jobs stuck in RUNNING (Zombie Nodes)
            # Since chunks don't hit the DB anymore (they go via Redis), we rely on 
            # `updated_at` which the Node should periodically bump, OR we check if the node 
            # disconnected entirely from the Redis presence system.
            # To keep V1 simple without schema migrations on Job.updated_at, we just assume
            # jobs running longer than a global maximum limit (e.g. 5 mins) without completing 
            # are zombies. In a real Series A, the Node Agent emits heartbeats to DB.
            base_timeout = now - timedelta(minutes=5)
            stalled_running = db.query(schema.Job).filter(
                schema.Job.status == schema.JobStatus.RUNNING,
                schema.Job.created_at < base_timeout
            ).all()
            
            for job in stalled_running:
                # Double check Redis to see if the node is still reporting as ONLINE
                if job.node_id:
                     node_status = redis_store.get_node_status(job.node_id)
                     if node_status != "ONLINE":
                          self._handle_stalled_job(db, job, "Node went OFFLINE during RUNNING")
                     else:
                          self._handle_stalled_job(db, job, "RUNNING timeout (Max Duration Exceeded)")
                else:
                     self._handle_stalled_job(db, job, "RUNNING but no node assigned?")

        finally:
            db.close()

    def _handle_stalled_job(self, db, job: schema.Job, reason: str):
        logger.warning(f"Watchdog triggered for Job {job.id} on Node {job.node_id}. Reason: {reason}")
        
        failed_node_id = job.node_id

        # 1. Punish the Node (Drop reputation, mark offline, or force reboot)
        if failed_node_id:
            node = db.query(schema.Node).filter(schema.Node.id == failed_node_id).first()
            if node:
                node.reputation_score = max(0, (node.reputation_score or 100) - 10)
                logger.warning(f"Slashed reputation of Node {failed_node_id} to {node.reputation_score}")
                
            # Free up the VRAM we reserved in Redis so it's not permanently lost
            req_vram = (job.parameters or {}).get("vram_required", 1)
            redis_store.release_node_capacity(failed_node_id, req_vram)

        # 2. Auto-Retry: Re-Queue the job unassigned for the Scheduler to pick up
        job.status = schema.JobStatus.QUEUED
        job.node_id = None
        
        # 3. Notify the user via SSE that a failover is happening
        redis_store.client.publish(f"job:{job.id}", '{"status": "Node connection lost. Rerouting to a new node..."}')
        
        db.commit()

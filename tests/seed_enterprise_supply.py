import uuid
import random
import os
import sys
from datetime import datetime, timedelta

# Ensure we can import the control_plane
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from control_plane.database import schema

def seed_cloud():
    schema.init_db()
    db = schema.SessionLocal()
    
    print("Seeding 50 Enterprise Cloud Nodes...")
    
    locations = ["us-east-1", "us-west-2", "eu-central-1", "ap-northeast-1", "sa-east-1"]
    gpus = [
        ("NVIDIA H100 80GB", 80960),
        ("NVIDIA A100 80GB", 80960),
        ("NVIDIA A100 40GB", 40480),
        ("NVIDIA RTX 4090", 24576)
    ]
    models = [
        "llama-3-8b",
        "mixtral-8x7b",
        "llama-3-70b"
    ]
    
    count = 0
    for i in range(50):
        node_id = str(uuid.uuid4())
        gpu_choice = random.choice(gpus)
        gpu_count = random.choice([4, 8])
        
        # Give them huge CPU/RAM to look like big instances
        cpu_cores = random.choice([64, 96, 128])
        memory_mb = random.choice([256000, 512000, 1024000])
        
        node = schema.Node(
            id=node_id,
            address=f"10.0.{random.randint(1,254)}.{random.randint(1,254)}:8000",
            cpu_cores=cpu_cores,
            memory_mb=memory_mb,
            gpu_model=gpu_choice[0],
            gpu_vram=gpu_choice[1],
            gpu_count=gpu_count,
            cuda_version="12.2",
            location=random.choice(locations),
            status=schema.NodeStatus.ONLINE,
            last_heartbeat=datetime.utcnow() - timedelta(seconds=random.randint(0, 30)),
            reputation_score=100.0,
            avg_ttft_ms=random.randint(40, 150)
        )
        
        wallet = schema.Wallet(
            node_id=node_id,
            pending_rewards=random.uniform(50.0, 500.0),
            withdrawable_balance=random.uniform(1000.0, 5000.0),
            compute_credits=random.uniform(100000.0, 500000.0)
        )
        
        db.add(node)
        db.add(wallet)
        
        # Load a random subset of models
        num_models = random.randint(1, 3)
        assigned_models = random.sample(models, num_models)
        
        for m in assigned_models:
            mc = schema.ModelCache(
                id=str(uuid.uuid4()),
                node_id=node_id,
                model_name=m,
                quantization="fp16",
                tensor_parallel_size=gpu_count if m == "llama-3-70b" else random.choice([1, 2, 4]),
                is_loaded=1
            )
            db.add(mc)
            
        count += 1

    db.commit()
    db.close()
    
    print(f"Successfully seeded {count} Enterprise nodes with their respective models and wallets.")

if __name__ == "__main__":
    seed_cloud()

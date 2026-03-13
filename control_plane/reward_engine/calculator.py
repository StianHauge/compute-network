from datetime import datetime
from sqlalchemy.orm import Session
from control_plane.database import schema

# Token-based AI Inference Pricing Model
PRICE_PER_TOKEN = 0.0010  # e.g., $1 per 1,000 tokens
REWARD_RATIO = 0.80       # 80% to node

def process_job_reward(job_id: str, node_id: str, tokens_generated: int, db: Session):
    node = db.query(schema.Node).filter(schema.Node.id == node_id).first()
    if not node:
        return
        
    job = db.query(schema.Job).filter(schema.Job.id == job_id).first()
    
    # Internal Nodes do not earn rewards and do not charge developers during bootstrap
    if node.node_type == schema.NodeType.INTERNAL:
        import logging
        logger = logging.getLogger("RewardEngine")
        logger.info(f"Skipping reward calculation for Internal Node {node_id}")
        return
        
    # Dynamic Pricing Oracle
    model_pricing = {
        "mistral-7b": 0.0005,
        "llama-3-8b": 0.0008,
        "mixtral-8x7b": 0.0020
    }
    price = model_pricing.get(job.model, PRICE_PER_TOKEN) if job else PRICE_PER_TOKEN
    
    total_value = tokens_generated * price
    node_reward_amt = total_value * REWARD_RATIO
    platform_fee = total_value - node_reward_amt
    
    # Deduct Compute Credits from Developer (The Caller)
    if job and job.caller_node_id:
        caller_wallet = db.query(schema.Wallet).filter(schema.Wallet.node_id == job.caller_node_id).first()
        if caller_wallet:
            caller_wallet.compute_credits -= total_value
            if caller_wallet.compute_credits < 0:
                caller_wallet.compute_credits = 0.0
    
    # Create the reward record
    reward = schema.Reward(
        job_id=job_id,
        node_id=node_id,
        amount=node_reward_amt,
        timestamp=datetime.utcnow()
    )
    db.add(reward)
    
    # Update the node's wallet
    wallet = db.query(schema.Wallet).filter(schema.Wallet.node_id == node_id).first()
    if wallet:
        wallet.pending_rewards += node_reward_amt
        wallet.compute_credits += node_reward_amt  # 1:1 match for compute credits
        # Automatic withdrawal logic check
        if wallet.pending_rewards >= 50.0:
            wallet.withdrawable_balance += wallet.pending_rewards
            wallet.pending_rewards = 0.0
            
            # Phase 5: Simulated Web3 On-Chain Minting
            import hashlib
            import logging
            tx_hash = "0x" + hashlib.sha256(f"mint_{node_id}_{wallet.withdrawable_balance}_{datetime.utcnow()}".encode()).hexdigest()
            logger = logging.getLogger("RewardEngine")
            logger.info(f"[WEB3] Minted {node_reward_amt} $AVR to wallet {node_id}")
            logger.info(f"[WEB3] Transaction Hash: {tx_hash}")
            
    db.commit()

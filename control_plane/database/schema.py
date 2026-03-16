from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import enum
from datetime import datetime

Base = declarative_base()

class NodeStatus(enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"

class NodeType(enum.Enum):
    INTERNAL = "INTERNAL"
    COMMUNITY = "COMMUNITY"

class JobStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Node(Base):
    __tablename__ = 'nodes'
    
    id = Column(String, primary_key=True, index=True)
    address = Column(String, unique=True, index=True)
    status = Column(Enum(NodeStatus), default=NodeStatus.ONLINE)
    node_type = Column(Enum(NodeType), default=NodeType.COMMUNITY)
    cpu_cores = Column(Integer)
    memory_mb = Column(Integer)
    gpu_model = Column(String, nullable=True)
    gpu_vram = Column(Integer, nullable=True) # in GB or MB. Let's say GB.
    gpu_count = Column(Integer, default=1)
    cuda_version = Column(String, nullable=True)
    location = Column(String)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    avg_ttft_ms = Column(Float, default=0.0) # Reputation/latency tracking
    reputation_score = Column(Integer, default=100) # Auditor-controlled network score (0-100)
    staked_avr = Column(Float, default=0.0) # Phase 4.4: Bonded Reputation Staking
    earned_avr = Column(Float, default=0.0) # Phase 4.4: Unsettled ledger balance
    
    jobs = relationship("Job", back_populates="node")
    wallet = relationship("Wallet", back_populates="node", uselist=False)
    cached_models = relationship("ModelCache", back_populates="node", cascade="all, delete-orphan")
    
    developer_id = Column(String, ForeignKey('developers.id'), nullable=True)
    developer = relationship("Developer", back_populates="nodes")

class ModelCache(Base):
    __tablename__ = 'model_cache'
    id = Column(String, primary_key=True, index=True)
    node_id = Column(String, ForeignKey('nodes.id'))
    model_name = Column(String, index=True)
    quantization = Column(String, default="fp16") # e.g., fp16, int8, int4, gguf
    tensor_parallel_size = Column(Integer, default=1)
    is_loaded = Column(Integer, default=1) # 1 if in VRAM, 0 if on disk
    
    node = relationship("Node", back_populates="cached_models")

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(String, primary_key=True, index=True)
    task_type = Column(String, nullable=False) # e.g. "llm_inference"
    model = Column(String, nullable=False)
    prompt = Column(String, nullable=True)
    messages = Column(JSON, nullable=True)
    parameters = Column(JSON, nullable=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    node_id = Column(String, ForeignKey('nodes.id'), nullable=True) # Node running the job
    caller_node_id = Column(String, nullable=True) # Node paying for the job (acting as API Key)
    result_logs = Column(String, nullable=True)
    ttft_ms = Column(Float, nullable=True) # Time to first token
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    node = relationship("Node", back_populates="jobs")

class Wallet(Base):
    __tablename__ = 'wallets'
    
    node_id = Column(String, ForeignKey('nodes.id'), primary_key=True)
    pending_rewards = Column(Float, default=0.0)
    withdrawable_balance = Column(Float, default=0.0)
    compute_credits = Column(Float, default=0.0) # Credits for running own inference
    
    node = relationship("Node", back_populates="wallet")

class Developer(Base):
    __tablename__ = 'developers'
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    api_key = Column(String, unique=True, index=True)
    node_link_key = Column(String, unique=True, index=True, nullable=True) # Used specifically for nodes to register under this dev
    compute_credits = Column(Float, default=50.0) # 50 free credits on sign up
    created_at = Column(DateTime, default=datetime.utcnow)
    
    nodes = relationship("Node", back_populates="developer")

class Reward(Base):
    __tablename__ = 'rewards'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(String, ForeignKey('jobs.id'))
    node_id = Column(String, ForeignKey('nodes.id'))
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

import os

# Use DATABASE_URL from .env or docker-compose, fallback to local sqlite if missing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./compute_network.db")

connect_args = {"check_same_thread": False, "timeout": 15} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

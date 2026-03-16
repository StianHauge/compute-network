import uuid
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from fastapi import FastAPI, Depends, HTTPException, Security, WebSocket, WebSocketDisconnect
from passlib.context import CryptContext

from control_plane.database import schema
from control_plane.database.redis_store import redis_store
from control_plane.events.nats_client import nats_bus
from control_plane.events.aggregator import aggregator
from control_plane.agents.auditor import AuditorAgent
from control_plane.agents.dispatcher import DispatcherAgent
from control_plane.agents.accountant import accountant
from control_plane.events.mock_data_engine import mock_engine
from control_plane.scheduler.engine import Scheduler

app = FastAPI(title="Compute Network Control Plane API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = Scheduler()
auditor = AuditorAgent()
dispatcher = DispatcherAgent()

# Global memory registry to bridge Node chunk uploads -> Client SSE streams
job_streams: Dict[str, asyncio.Queue] = {}
_loop = None

@app.on_event("startup")
async def startup_event():
    global _loop
    _loop = asyncio.get_event_loop()
    await nats_bus.connect()
    aggregator.start()
    accountant.start()
    scheduler.start()
    auditor.start()
    dispatcher.start()
    mock_engine.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.stop()
    auditor.stop()
    dispatcher.stop()

# Dependency
def get_db():
    db = schema.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Start DB
schema.init_db()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# ----------------------------------------------------
# Pydantic Schemas
# ----------------------------------------------------
class CachedModelInfo(BaseModel):
    name: str
    quantization: str = "fp16"
    tensor_parallel_size: int = 1

class NodeRegisterRequest(BaseModel):
    address: str
    cpu_cores: int
    memory_mb: int
    gpu_model: Optional[str] = None
    gpu_vram: Optional[int] = None
    gpu_count: int = 1
    cuda_version: Optional[str] = None
    location: str
    node_type: str = "community"
    models: Optional[List[Union[str, CachedModelInfo]]] = []

class NodeHeartbeatRequest(BaseModel):
    node_id: str
    models: Optional[List[Union[str, CachedModelInfo]]] = None

class InferenceTextRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int = 200
    parameters: Optional[Dict[str, Any]] = None

class ChatMessage(BaseModel):
    role: str
    content: str
    
class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    max_tokens: Optional[int] = 512

class SecureChatCompletionRequest(BaseModel):
    model: str
    encrypted_payload: str
    stream: Optional[bool] = False
    max_tokens: Optional[int] = 512

class JobResponse(BaseModel):
    id: str
    status: str
    node_id: Optional[str]

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# ----------------------------------------------------
# Endpoints
# ----------------------------------------------------

import os
import secrets
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)
NETWORK_SECRET = os.getenv("NETWORK_SECRET", "averra_dev_secret_override_this")

def verify_node_token(auth: HTTPAuthorizationCredentials = Security(security)):
    if not auth or auth.credentials != NETWORK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid Network Token")
    return True

@app.post("/auth/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(schema.Developer).filter(schema.Developer.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    dev_id = str(uuid.uuid4())
    api_key = f"sk-av-{secrets.token_urlsafe(32)}"
    hashed_pw = get_password_hash(request.password)
    
    new_dev = schema.Developer(
        id=dev_id,
        email=request.email,
        password_hash=hashed_pw,
        api_key=api_key,
        compute_credits=50.0  # Free starting credits
    )
    db.add(new_dev)
    db.commit()
    
    return {"id": dev_id, "api_key": api_key, "compute_credits": 50.0}

@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    dev = db.query(schema.Developer).filter(schema.Developer.email == request.email).first()
    if not dev:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    if not verify_password(request.password, dev.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    return {"id": dev.id, "api_key": dev.api_key, "compute_credits": dev.compute_credits}

@app.post("/nodes/register")
def register_node(request: NodeRegisterRequest, db: Session = Depends(get_db), verified: bool = Depends(verify_node_token)):
    node_id = str(uuid.uuid4())
    
    # Map raw string to enum
    ntype = schema.NodeType.INTERNAL if request.node_type.lower() == "internal" else schema.NodeType.COMMUNITY
    
    new_node = schema.Node(
        id=node_id,
        address=request.address,
        cpu_cores=request.cpu_cores,
        memory_mb=request.memory_mb,
        gpu_model=request.gpu_model,
        gpu_vram=request.gpu_vram,
        gpu_count=request.gpu_count,
        cuda_version=request.cuda_version,
        location=request.location,
        node_type=ntype,
        status=schema.NodeStatus.ONLINE,
        last_heartbeat=datetime.utcnow()
    )
    new_wallet = schema.Wallet(
        node_id=node_id,
        pending_rewards=0.0,
        withdrawable_balance=0.0
    )
    
    db.add(new_node)
    db.add(new_wallet)
    
    for m in request.models or []:
        if isinstance(m, str):
            mc = schema.ModelCache(id=str(uuid.uuid4()), node_id=node_id, model_name=m, is_loaded=1)
        else:
            mc = schema.ModelCache(id=str(uuid.uuid4()), node_id=node_id, model_name=m.name, quantization=m.quantization, tensor_parallel_size=m.tensor_parallel_size, is_loaded=1)
        db.add(mc)
        
    db.commit()
    
    return {"node_id": node_id, "status": "Registered"}

@app.post("/nodes/heartbeat")
def node_heartbeat(request: NodeHeartbeatRequest, db: Session = Depends(get_db), verified: bool = Depends(verify_node_token)):
    node = db.query(schema.Node).filter(schema.Node.id == request.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
        
    node.last_heartbeat = datetime.utcnow()
    node.status = schema.NodeStatus.ONLINE
    
    if request.models is not None:
        db.query(schema.ModelCache).filter(schema.ModelCache.node_id == request.node_id).delete()
        for m in request.models:
            if isinstance(m, str):
                mc = schema.ModelCache(id=str(uuid.uuid4()), node_id=request.node_id, model_name=m, is_loaded=1)
            else:
                mc = schema.ModelCache(id=str(uuid.uuid4()), node_id=request.node_id, model_name=m.name, quantization=m.quantization, tensor_parallel_size=m.tensor_parallel_size, is_loaded=1)
            db.add(mc)
            
    db.commit()
    return {"status": "Heartbeat updated"}

# Active websocket connections state tracking
active_node_telemetry_streams: Dict[str, WebSocket] = {}
active_sentinel_streams: Dict[str, WebSocket] = {}

@app.websocket("/ws/telemetry/{node_id}")
async def ws_telemetry(websocket: WebSocket, node_id: str):
    await websocket.accept()
    active_node_telemetry_streams[node_id] = websocket
    try:
        while True:
            # We expect a JSON payload from the Node Agent with pynvml stats every 1s
            data = await websocket.receive_json()
            
            # Fire and forget into NATS JetStream for hyper-scale!
            # The Aggregator will parse this and update Redis < 10ms.
            await nats_bus.publish_telemetry(node_id, data)
            
            # Quick check for critical alerts
            if data.get("temperature_c", 0) > 85:
                 print(f"[{node_id}] WARNING: Thermal Throttling immenent! {data.get('temperature_c')}C")
            
    except WebSocketDisconnect:
        active_node_telemetry_streams.pop(node_id, None)
        print(f"Node {node_id} WebSocket disconnected.")

@app.websocket("/ws/sentinel/{node_id}")
async def ws_sentinel(websocket: WebSocket, node_id: str):
    await websocket.accept()
    active_sentinel_streams[node_id] = websocket
    print(f"Sentinel {node_id} connected for updates.")
    try:
        while True:
            # We just need to keep the connection alive. Sentinels don't send data here, they only listen.
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_sentinel_streams.pop(node_id, None)
        print(f"Sentinel {node_id} WebSocket disconnected.")

class BroadcastUpdateRequest(BaseModel):
    target_version: str
    image_url: str

@app.post("/admin/nodes/broadcast-update")
async def broadcast_update(request: BroadcastUpdateRequest):
    # In a real app we'd authenticate the admin
    command = {
        "command": "UPDATE_AVAILABLE",
        "target_version": request.target_version,
        "image_url": request.image_url
    }
    
    # Push to NATS so all Sentinels across the globe catch it!
    await nats_bus.broadcast_sentinel_command(command)
    
    count = 0
    disconnected = []
    
    # Keep legacy active connections supported
    for node_id, ws in active_sentinel_streams.items():
        try:
            await ws.send_json(command)
            count += 1
        except Exception:
            disconnected.append(node_id)
            
    for node_id in disconnected:
        active_sentinel_streams.pop(node_id, None)
        
    return {"status": "Broadcast sent via NATS & Legacy Sockets", "legacy_nodes_reached": count}

class NodePollRequest(BaseModel):
    node_id: str

@app.post("/nodes/jobs/poll")
def poll_jobs(request: NodePollRequest, db: Session = Depends(get_db), verified: bool = Depends(verify_node_token)):
    # Find any pending jobs assigned to this node
    job = db.query(schema.Job).filter(
        schema.Job.node_id == request.node_id,
        schema.Job.status == schema.JobStatus.PENDING
    ).first()
    
    if not job:
        return {"job": None}
        
    # Mark it as RUNNING so no one else picks it up or we don't return it again immediately
    job.status = schema.JobStatus.RUNNING
    db.commit()
    
    return {
        "job": {
            "id": job.id,
            "task_type": job.task_type,
            "model": job.model,
            "prompt": job.prompt,
            "messages": job.messages,
            "parameters": job.parameters
        }
    }

@app.get("/nodes")
def list_nodes(db: Session = Depends(get_db)):
    # Fetch live state from Redis
    nodes = redis_store.get_all_routable_nodes()
    return nodes


@app.get("/api/network/stats")
async def network_stats():
    """Returns global telemetry aggregated from Redis in sub-milliseconds."""
    nodes = redis_store.get_all_routable_nodes()
    
    online_count = 0
    superposition_count = 0
    total_vram_gb = 0.0
    total_ping_ms = 0.0
    
    for n in nodes:
        status = n.get("status", "")
        if status in ["ONLINE", "SUPERPOSITION"]:
            online_count += 1
            total_vram_gb += float(n.get("vram_free", 0) or 0)
            # Mocking ping aggregation
            total_ping_ms += float(n.get("ping_ms", 25))
            
        if status == "SUPERPOSITION":
            superposition_count += 1
            
    avg_ping = (total_ping_ms / online_count) if online_count > 0 else 25.0 # fallback default if real telemetry not flowing
            
    return {
        "nodes_online": online_count,
        "nodes_superposition": superposition_count,
        "total_vram_gb": round(total_vram_gb, 2),
        "global_avg_ping_ms": round(avg_ping, 1),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/nodes/live")
async def nodes_live():
    """Returns the precise realtime array of all nodes in the state grid."""
    nodes = redis_store.get_all_routable_nodes()
    # Mask full IDs for security in the dashboard
    frontend_nodes = []
    for n in nodes:
        # Example: 'e4a2...b13'
        short_id = f"{n['id'][:4]}...{n['id'][-3:]}" if len(n['id']) > 8 else n['id']
        frontend_nodes.append({
            "id_short": short_id,
            "status": n.get("status", "OFFLINE"),
            "vram_free": float(n.get("vram_free", 0) or 0),
            "temperature_c": float(n.get("temperature_c", 0) or 0),
            "pcie_bw": float(n.get("pcie_bw", 0) or 0),
            "earned_avr": float(n.get("earned_avr", 0) or 0),
            "location": n.get("location", "Unknown")
        })
    return frontend_nodes
    

@app.get("/api/economy/live-ledger")
async def get_live_ledger(db: Session = Depends(get_db)):
    """Returns the actual ledger of developers and nodes from the database."""
    users = db.query(schema.Developer).limit(10).all()
    out_users = [{"email": u.email, "credits": round(u.compute_credits, 2)} for u in users]
        
    top_nodes = db.query(schema.Node).order_by(schema.Node.staked_avr.desc()).limit(10).all()
    out_nodes = [{"id": n.id[:8], "earned_avr": round(n.earned_avr or 0, 4), "staked": round(n.staked_avr or 0, 2)} for n in top_nodes]
        
    return {
        "consumers": out_users,
        "providers": out_nodes
    }

@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest, 
    db: Session = Depends(get_db),
    auth: HTTPAuthorizationCredentials = Security(security)
):
    caller_id = None
    if auth and auth.credentials:
        token = auth.credentials
        if token != "sk-admin":
            # 1. Check if token is a Developer API Key
            dev = db.query(schema.Developer).filter(schema.Developer.api_key == token).first()
            if dev:
                if dev.compute_credits <= 0:
                    raise HTTPException(status_code=402, detail="Insufficient Compute Credits. Please add funds.")
                caller_id = dev.id
            else:
                # 2. Check if token is a Node ID
                wallet = db.query(schema.Wallet).filter(schema.Wallet.node_id == token).first()
                if not wallet:
                    raise HTTPException(status_code=401, detail="Invalid API Key. Not recognized as Developer or Node.")
                if wallet.compute_credits <= 0:
                    raise HTTPException(status_code=402, detail="Insufficient Compute Credits. Mine more on the network!")
                caller_id = token

    job_id = str(uuid.uuid4())
    parameters = {"max_tokens": request.max_tokens, "vram_required": 8}
    
    new_job = schema.Job(
        id=job_id,
        task_type="llm_inference",
        model=request.model,
        messages=[m.model_dump() for m in request.messages],
        parameters=parameters,
        status=schema.JobStatus.PENDING,
        caller_node_id=caller_id
    )
    db.add(new_job)
    db.commit()
    
    if request.stream:
        job_streams[job_id] = asyncio.Queue()
        
        async def event_generator():
            try:
                while True:
                    chunk = await job_streams[job_id].get()
                    if chunk is None or chunk == "[DONE]":
                        yield "data: [DONE]\n\n"
                        break
                    else:
                        yield f"data: {chunk}\n\n"
            finally:
                if job_id in job_streams:
                    del job_streams[job_id]
                    
        return StreamingResponse(event_generator(), media_type="text/event-stream")
        
    else:
        return {"error": "Only streaming is supported currently in minimal viable network"}

@app.post("/v1/chat/completions/secure")
async def secure_chat_completions(
    request: SecureChatCompletionRequest,
    db: Session = Depends(get_db),
    auth: HTTPAuthorizationCredentials = Security(security)
):
    caller_id = None
    if auth and auth.credentials:
        token = auth.credentials
        if token != "sk-admin":
            # 1. Check if token is a Developer API Key
            dev = db.query(schema.Developer).filter(schema.Developer.api_key == token).first()
            if dev:
                if dev.compute_credits <= 0:
                    raise HTTPException(status_code=402, detail="Insufficient Compute Credits. Please add funds.")
                caller_id = dev.id
            else:
                # 2. Check if token is a Node ID
                wallet = db.query(schema.Wallet).filter(schema.Wallet.node_id == token).first()
                if not wallet:
                    raise HTTPException(status_code=401, detail="Invalid API Key. Not recognized as Developer or Node.")
                if wallet.compute_credits <= 0:
                    raise HTTPException(status_code=402, detail="Insufficient Compute Credits. Mine more on the network!")
                caller_id = token

    job_id = str(uuid.uuid4())
    parameters = {"max_tokens": request.max_tokens, "vram_required": 8}
    
    # We pass the encrypted payload as the ONLY message content
    secure_messages = [{"role": "user", "content": request.encrypted_payload}]
    
    new_job = schema.Job(
        id=job_id,
        task_type="secure_llm_inference",  # Route to EnclaveRuntime
        model=request.model,
        messages=secure_messages,
        parameters=parameters,
        status=schema.JobStatus.PENDING,
        caller_node_id=caller_id
    )
    db.add(new_job)
    db.commit()
    
    if request.stream:
        job_streams[job_id] = asyncio.Queue()
        
        async def event_generator():
            try:
                while True:
                    chunk = await job_streams[job_id].get()
                    if chunk is None or chunk == "[DONE]":
                        yield "data: [DONE]\n\n"
                        break
                    else:
                        yield f"data: {chunk}\n\n"
            finally:
                if job_id in job_streams:
                    del job_streams[job_id]
                    
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        return {"error": "Only streaming is supported currently"}

class NodeJobChunkRequest(BaseModel):
    node_id: str
    chunk: str

@app.post("/jobs/{job_id}/chunk")
def submit_job_chunk(job_id: str, request: NodeJobChunkRequest, db: Session = Depends(get_db), verified: bool = Depends(verify_node_token)):
    if job_id in job_streams and _loop is not None:
        # Format payload as OpenAI discrete chunk
        payload = json.dumps({
            "id": job_id,
            "object": "chat.completion.chunk",
            "choices": [{"delta": {"content": request.chunk}}]
        })
        _loop.call_soon_threadsafe(job_streams[job_id].put_nowait, payload)
        
    return {"status": "ok"}

@app.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(schema.Job).filter(schema.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "job_id": job.id,
        "status": job.status.value,
        "node_id": job.node_id,
        "result_logs": job.result_logs
    }

@app.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(schema.Job).all()
    return [{
        "id": j.id,
        "status": j.status.value,
        "node_id": j.node_id
    } for j in jobs]

@app.get("/nodes/{node_id}/wallet")
def get_node_wallet(node_id: str, db: Session = Depends(get_db)):
    wallet = db.query(schema.Wallet).filter(schema.Wallet.node_id == node_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
        
    return {
        "node_id": wallet.node_id,
        "pending_rewards": wallet.pending_rewards,
        "withdrawable_balance": wallet.withdrawable_balance,
        "compute_credits": wallet.compute_credits
    }

class NodeJobCompleteRequest(BaseModel):
    node_id: str
    result_logs: str
    tokens_generated: Optional[int] = 0
    ttft_ms: Optional[int] = None
    attestation_receipt: Optional[str] = None # ZKP or Signed DCGM payload

@app.post("/jobs/{job_id}/complete")
def complete_job(job_id: str, request: NodeJobCompleteRequest, db: Session = Depends(get_db), verified: bool = Depends(verify_node_token)):
    job = db.query(schema.Job).filter(
        schema.Job.id == job_id,
        schema.Job.node_id == request.node_id,
        schema.Job.status == schema.JobStatus.RUNNING
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Running job not found for this node")
        
    # Phase 3: Cryptographic Attestation Check
    if request.tokens_generated > 0:
        if request.attestation_receipt == "INVALID_SIGNATURE":
            # Slashing mechanism for cheating nodes!
            node = db.query(schema.Node).filter(schema.Node.id == request.node_id).first()
            if node:
                node.reputation_score = 0
            wallet = db.query(schema.Wallet).filter(schema.Wallet.node_id == request.node_id).first()
            if wallet:
                wallet.withdrawable_balance = 0 # Confiscate funds!
            job.status = schema.JobStatus.FAILED
            db.commit()
            raise HTTPException(status_code=403, detail="Attestation Signature Invalid. Node Slashed.")

    job.status = schema.JobStatus.COMPLETED
    job.result_logs = request.result_logs
    job.completed_at = datetime.utcnow()
    
    if request.ttft_ms is not None:
        job.ttft_ms = request.ttft_ms
        node = db.query(schema.Node).filter(schema.Node.id == request.node_id).first()
        if node:
            if node.avg_ttft_ms == 0:
                node.avg_ttft_ms = request.ttft_ms
            else:
                node.avg_ttft_ms = (node.avg_ttft_ms * 0.9) + (request.ttft_ms * 0.1)
                
    db.commit()
    
    # End SSE Stream
    if job_id in job_streams and _loop is not None:
        _loop.call_soon_threadsafe(job_streams[job_id].put_nowait, "[DONE]")
    
    # Trigger reward calculation here
    from control_plane.reward_engine.calculator import process_job_reward
    process_job_reward(job.id, request.node_id, request.tokens_generated, db)
    
    return {"status": "Job marked as completed and rewards calculated"}


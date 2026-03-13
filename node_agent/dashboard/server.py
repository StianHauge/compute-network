import threading
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, StreamingResponse
import requests
import uvicorn
import logging
from pydantic import BaseModel
from typing import List, Dict, Any

logger = logging.getLogger("NodeDashboard")

app = FastAPI(title="Node Agent Local Dashboard")

# Global ref to agent so dashboard can read hardware and node_id
node_agent_ref = None

CONTROL_PLANE_URL = "http://127.0.0.1:8000"

class P2PPingResponse(BaseModel):
    node_id: str
    models: List[str]
    status: str

@app.get("/p2p/ping", response_model=P2PPingResponse)
def p2p_ping():
    if not node_agent_ref:
        return {"node_id": "unknown", "models": [], "status": "offline"}
    return {
        "node_id": node_agent_ref.node_id or "unregistered",
        "models": node_agent_ref.cached_models,
        "status": "online"
    }

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    max_tokens: int = 100
    stream: bool = False

@app.post("/v1/chat/completions")
def direct_chat_completion(req: ChatCompletionRequest):
    if not node_agent_ref:
        raise HTTPException(status_code=503, detail="Node agent is not running")
        
    if req.model not in node_agent_ref.cached_models:
        raise HTTPException(status_code=400, detail=f"Model {req.model} not available on this node")
        
    import os
    from node_agent.agent.core import VLLMRuntime, SimulatedRuntime
    
    # Direct inference bypassing Control Plane
    try:
        runtime = VLLMRuntime() if os.getenv("USE_VLLM") == "true" else SimulatedRuntime(node_agent_ref.node_id)
        
        def stream_generator():
            for chunk in runtime.execute(req.model, req.messages, req.max_tokens):
                # Basic escaping for SSE
                safe_chunk = chunk.replace('"', '\\"').replace('\n', '\\n')
                yield f'data: {{"choices": [{{"delta": {{"content": "{safe_chunk}"}}}}]}}\n\n'
            yield "data: [DONE]\n\n"
            
        return StreamingResponse(stream_generator(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"P2P Inference failed: {e}")
        raise HTTPException(status_code=500, detail="Inference execution failed")

def get_node_stats():
    if not node_agent_ref or not node_agent_ref.node_id:
        return {"error": "Node not registered yet."}
        
    try:
        # Fetch wallet info from control plane (or we could cache it in the agent)
        # We need an endpoint for this, so let's mock it for now
        # Actually, let's just make a quick request to the control plane
        resp = requests.get(f"{CONTROL_PLANE_URL}/nodes/{node_agent_ref.node_id}/wallet")
        if resp.status_code == 200:
            wallet = resp.json()
        else:
            wallet = {"pending_rewards": 0.0, "withdrawable_balance": 0.0}
            
        return {
            "node_id": node_agent_ref.node_id,
            "hardware": node_agent_ref.hardware.model_dump(),
            "wallet": wallet
        }
    except Exception as e:
        logger.error(f"Error fetching stats for dashboard: {e}")
        return {"error": "Could not fetch stats"}

@app.get("/", response_class=HTMLResponse)
def index():
    stats = get_node_stats()
    if "error" in stats:
        return f"<html><body><h1>Node Dashboard</h1><p>{stats['error']}</p></body></html>"
        
    hw = stats["hardware"]
    w = stats["wallet"]
    
    html = f"""
    <html>
        <head>
            <title>Node Agent Dashboard</title>
            <style>
                body {{ font-family: sans-serif; margin: 40px; background: #f4f4f9; }}
                .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
                h1, h2 {{ color: #333; }}
                .stat {{ font-size: 1.2em; margin: 10px 0; }}
            </style>
            <meta http-equiv="refresh" content="5">
        </head>
        <body>
            <h1>Node Agent Dashboard</h1>
            <div class="card">
                <h2>Node Info</h2>
                <div class="stat"><strong>ID:</strong> {stats['node_id']}</div>
                <div class="stat"><strong>CPU Cores:</strong> {hw['cpu_cores']}</div>
                <div class="stat"><strong>Memory:</strong> {hw['memory_mb']} MB</div>
                <div class="stat"><strong>GPU:</strong> {hw['gpu_model'] or 'None'}</div>
            </div>
            
            <div class="card">
                <h2>Earnings (Auto-refreshes)</h2>
                <div class="stat"><strong>Pending Rewards:</strong> ${w['pending_rewards']:.2f}</div>
                <div class="stat"><strong>Withdrawable Balance:</strong> ${w['withdrawable_balance']:.2f}</div>
                <div class="stat"><strong>Total Earned:</strong> ${(w['pending_rewards'] + w['withdrawable_balance']):.2f}</div>
            </div>
        </body>
    </html>
    """
    return html

import os

def start_dashboard(agent):
    global node_agent_ref
    node_agent_ref = agent
    
    port = int(os.environ.get("DASHBOARD_PORT", 8080))
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")
        
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    return t

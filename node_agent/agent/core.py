import os
import time
import requests
import logging
import docker
import asyncio
import websockets
import json
import threading
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    import pynvml
    HAS_NVML = True
except ImportError:
    HAS_NVML = False
    
from pydantic import BaseModel
from typing import Optional

from node_agent.agent.ipc import IPCProvider, IPCConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NodeAgent")

CONTROL_PLANE_URL = os.getenv("CONTROL_PLANE_URL", "https://averra.network")
NODE_AUTH_TOKEN = os.getenv("NODE_AUTH_TOKEN", "averra_dev_secret_override_this")

class HardwareInfo(BaseModel):
    cpu_cores: int
    memory_mb: int
    gpu_model: Optional[str] = None
    gpu_vram: Optional[int] = None
    cuda_version: Optional[str] = None
    location: str = "local"
    temperature_c: Optional[int] = 0
    pcie_bw_usage: Optional[float] = 0.0

class InferenceRuntime:
    def __init__(self):
        self.device = 'cuda' if HAS_TORCH and torch.cuda.is_available() else 'cpu'
        self.ipc_provider = IPCProvider()
        self.ipc_provider.start()
        
        # 1. Phase 3: Try to Superposition VRAM!
        inherited_weights = IPCConsumer.fetch_shared_tensors()
        if inherited_weights and HAS_TORCH:
            self.model_weights = inherited_weights['mistral-7b']
            logger.info(f"SUPERPOSITION READY! Using existing VRAM allocations on {self.device}. Shape: {self.model_weights.shape}")
        else:
            logger.info(f"COLD BOOT... Allocating 1GB of simulated Mistral-7b weights in {self.device}...")
            # Simulate a 1GB model weight tensor (250 million 32-bit floats)
            if HAS_TORCH:
                self.model_weights = torch.ones(250000000, dtype=torch.float32, device=self.device)
                # 2. Tell the daemon we have weights available for subsequent containers
                self.ipc_provider.register_tensor('mistral-7b', self.model_weights)
            else:
                self.model_weights = None

    def execute(self, model: str, messages: list, max_tokens: int):
        pass

class VLLMRuntime(InferenceRuntime):
    def __init__(self, port=8081):
        self.port = port
        self.endpoint = f"http://127.0.0.1:{port}/v1/chat/completions"
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.error(f"Docker SDK initialization failed: {e}")
            self.docker_client = None
            
    def _ensure_container_running(self, model: str):
        if not self.docker_client:
            logger.warning("Docker client unavailable. Attempting generic proxy...")
            return
            
        container_name = f"averra-vllm-{model.replace('/', '-')}"
        
        try:
            container = self.docker_client.containers.get(container_name)
            if container.status != "running":
                logger.info(f"Starting stopped container {container_name}...")
                container.start()
                time.sleep(10)
            return
        except docker.errors.NotFound:
            logger.info(f"Deploying new vLLM container for {model}...")
            hf_cache = os.path.expanduser("~/.cache/huggingface")
            os.makedirs(hf_cache, exist_ok=True)
            
            try:
                # Device requests enable NVIDIA Container Toolkit passthrough
                device_requests = [docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])]
                
                self.docker_client.containers.run(
                    "vllm/vllm-openai:latest",
                    command=f"--model {model} --host 0.0.0.0 --port 8000",
                    name=container_name,
                    ports={'8000/tcp': self.port},
                    volumes={hf_cache: {'bind': '/root/.cache/huggingface', 'mode': 'rw'}},
                    device_requests=device_requests,
                    detach=True
                )
                logger.info("vLLM container started. Waiting for model to load into VRAM...")
                time.sleep(15) # Wait for model weights to load
            except Exception as e:
                logger.error(f"Failed to deploy vLLM container: {e}")

    def execute(self, model: str, messages: list, max_tokens: int):
        self._ensure_container_running(model)
        
        # Forward compatible with OpenAI API spec from Ollama or vLLM running locally!
        import json
        payload = {
            "model": model, "messages": messages, "max_tokens": max_tokens, "stream": True
        }
        with requests.post(self.endpoint, json=payload, stream=True) as resp:
            for line in resp.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            content = json.loads(data_str).get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except:
                            pass

class SimulatedRuntime(InferenceRuntime):
    def __init__(self, node_id: str):
        self.node_id = node_id
        
    def execute(self, model: str, messages: list, max_tokens: int):
        words = ["This ", "is ", "a ", "streamed ", "AI ", "response ", "from ", "the ", "Averra ", "Network ", "node ", f"({self.node_id[:8]})!"]
        for w in words:
            time.sleep(0.1) # Simulate token generation speed
            yield w

import base64
import json

class EnclaveRuntime(InferenceRuntime):
    """
    Simulates a Trusted Execution Environment (AWS Nitro Enclaves / NVIDIA Confidential Computing).
    Host Node cannot read the plaintext input or output; only the enclave memory has the KMS keys.
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self._inner_runtime = SimulatedRuntime(node_id)
        
    def _decrypt_in_enclave(self, encrypted_payload: str) -> list:
        logger.info("[🛡️ TEE ENCLAVE] Accessing secure memory space...")
        logger.info("[🛡️ TEE ENCLAVE] Decrypting payload using KMS derived keys...")
        time.sleep(0.5) # Simulate KMS decryption latency
        try:
            decoded = base64.b64decode(encrypted_payload).decode('utf-8')
            return json.loads(decoded)
        except:
            return [{"role": "user", "content": "Decryption Failed"}]
            
    def _encrypt_in_enclave(self, text: str) -> str:
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
        
    def execute(self, model: str, messages: list, max_tokens: int):
        # We expect the 'messages' to be a single system/user prompt containing the encrypted base64 payload
        encrypted_text = messages[0].get("content", "")
        
        logger.info(f"[HOST] Node received opaque payload: {encrypted_text[:20]}... forwarding to TEE Enclave.")
        decrypted_messages = self._decrypt_in_enclave(encrypted_text)
        
        logger.info("[🛡️ TEE ENCLAVE] Inference running on plaintext Data in Secure Enclave...")
        
        for chunk in self._inner_runtime.execute(model, decrypted_messages, max_tokens):
            # Encrypt the memory stream BEFORE it exits the enclave to the Host CPU
            yield f"[ENCRYPTED_CHUNK] {self._encrypt_in_enclave(chunk)}"

class NodeAgent:
    def __init__(self):
        self.node_id = None
        self.is_running = False
        self.hardware = self._detect_hardware()
        # Pre-seed with models so it can serve the simulation out of the box
        # We explicitly omit llama-3-8b to test the Dispatcher Agent's scale-up logic
        self.cached_models = ["mistral-7b", "mixtral-8x7b"]

    def _detect_hardware(self) -> HardwareInfo:
        cores = os.cpu_count() or 4
        # Rough system memory in MB
        mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') if hasattr(os, 'sysconf') else 16*1024*1024*1024
        mem_mb = int(mem_bytes / (1024 * 1024))
        
        gpu_model = "Unknown/No GPU"
        gpu_vram = 0
        
        if HAS_NVML:
            try:
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                gpu_model = pynvml.nvmlDeviceGetName(handle)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_vram = int(info.total / (1024 * 1024 * 1024)) # GB
            except Exception as e:
                logger.error(f"NVML init failed: {e}")
        elif os.getenv("CLOUD_NODE") == "1":
            gpu_model = "8x H100 Cluster"
            gpu_vram = 640
            
        return HardwareInfo(
            cpu_cores=cores,
            memory_mb=mem_mb,
            gpu_model=gpu_model,
            gpu_vram=gpu_vram,
            location=os.getenv("NODE_LOCATION", "local-machine")
        )

    def _get_live_telemetry(self) -> dict:
        temp_c = 0
        pcie_rx = 0
        pcie_tx = 0
        if HAS_NVML:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                temp_c = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                pcie_tx = pynvml.nvmlDeviceGetPcieThroughput(handle, pynvml.NVML_PCIE_UTIL_TX_BYTES)
                pcie_rx = pynvml.nvmlDeviceGetPcieThroughput(handle, pynvml.NVML_PCIE_UTIL_RX_BYTES)
            except:
                pass
                
        hw_dump = self.hardware.model_dump()
        hw_dump["temperature_c"] = temp_c
        hw_dump["pcie_bw_usage"] = (pcie_tx + pcie_rx) / 1024.0 # KB/s
        
        import platform
        if platform.system() == "Darwin" and not (self.hardware.gpu_vram and self.hardware.gpu_vram > 0):
            import subprocess
            try:
                # Intel/AMD Macs have dedicated VRAM listed in system_profiler
                sp = subprocess.check_output(['system_profiler', 'SPDisplaysDataType']).decode()
                max_vram_gb = 0.0
                for line in sp.split('\n'):
                    if 'VRAM' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            val = parts[1].strip().split(' ')[0]
                            if 'GB' in line:
                                v = float(val)
                            elif 'MB' in line:
                                v = float(val) / 1024.0
                            else:
                                v = 0.0
                            if v > max_vram_gb:
                                max_vram_gb = v
                
                if max_vram_gb > 0:
                    hw_dump["vram_free"] = max_vram_gb
                else: # Fallback to Unified Memory if no discrete VRAM listed
                    pagesize = int(subprocess.check_output(['sysctl', '-n', 'hw.pagesize']).strip())
                    vm_stat = subprocess.check_output(['vm_stat']).decode()
                    free_pages = sum(int(l.split(':')[1].strip().strip('.')) for l in vm_stat.split('\n') if 'Pages free:' in l or 'Pages inactive:' in l)
                    hw_dump["vram_free"] = float((free_pages * pagesize) / (1024 ** 3))
            except Exception as e:
                hw_dump["vram_free"] = 0.0
        else:
            hw_dump["vram_free"] = self.hardware.gpu_vram if (self.hardware.gpu_vram and self.hardware.gpu_vram > 0) else 0.0
        
        return hw_dump

    def register(self):
        logger.info("Registering with Control Plane...")
        payload = self.hardware.model_dump()
        payload["address"] = f"127.0.0.1-mock-{os.getpid()}"
        payload["models"] = self.cached_models
        payload["node_type"] = os.getenv("NODE_TYPE", "community")
        headers = {}
        if NODE_AUTH_TOKEN:
            headers["Authorization"] = f"Bearer {NODE_AUTH_TOKEN}"
            
        resp = requests.post(f"{CONTROL_PLANE_URL}/nodes/register", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        self.node_id = data["node_id"]
        logger.info(f"Registered successfully! Node ID: {self.node_id}")

    async def _telemetry_stream_loop(self):
        ws_url = CONTROL_PLANE_URL.replace("http://", "ws://").replace("https://", "wss://")
        uri = f"{ws_url}/ws/telemetry/{self.node_id}"
        
        while self.is_running:
            try:
                async with websockets.connect(uri) as websocket:
                    logger.info("Connected to Control Plane Telemetry WebSocket.")
                    while self.is_running:
                        payload = self._get_live_telemetry()
                        await websocket.send(json.dumps(payload))
                        await asyncio.sleep(1) # Stream 1Hz
            except Exception as e:
                logger.warning(f"WebSocket disconnected. Retrying in 5s... ({e})")
                await asyncio.sleep(5)

    def start_telemetry(self):
        def run_async():
            asyncio.run(self._telemetry_stream_loop())
        t = threading.Thread(target=run_async, daemon=True)
        t.start()

    def poll_for_jobs(self):
        if not self.node_id:
            return
        try:
            headers = {}
            if NODE_AUTH_TOKEN:
                headers["Authorization"] = f"Bearer {NODE_AUTH_TOKEN}"
                
            resp = requests.post(f"{CONTROL_PLANE_URL}/nodes/jobs/poll", json={"node_id": self.node_id}, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            job = data.get("job")
            if job:
                logger.info(f"Received job: {job['id']}")
                self.execute_job(job)
        except Exception as e:
            logger.error(f"Error polling for jobs: {e}")

    def execute_job(self, job: dict):
        model_name = job.get('model', 'unknown-model')
        task_type = job.get('task_type', 'llm_inference')
        
        if task_type == 'preload_model':
            logger.info(f"Dispatcher ordered background preload for model: {model_name}")
            time.sleep(2) # simulate large download
            if model_name not in self.cached_models:
                self.cached_models.append(model_name)
            
            try:
                payload = {"node_id": self.node_id, "result_logs": "Preload completed", "tokens_generated": 0, "ttft_ms": 0}
                headers = {}
                if NODE_AUTH_TOKEN:
                    headers["Authorization"] = f"Bearer {NODE_AUTH_TOKEN}"
                    
                requests.post(f"{CONTROL_PLANE_URL}/jobs/{job['id']}/complete", json=payload, headers=headers)
            except Exception as e:
                logger.error(f"Failed to report preload completion: {e}")
            return
            
        logger.info(f"Received Inference Request for model: {model_name}. Task Type: {task_type}")
        
        if model_name not in self.cached_models:
            logger.info(f"Model {model_name} not found locally. Downloading weights to cache...")
            time.sleep(1) # simulate model download
            self.cached_models.append(model_name)
            logger.info("Model cached successfully.")
        
        # Determine the runtime
        if task_type == 'secure_llm_inference':
            logger.info("🔒 Routing job to Trusted Execution Environment (EnclaveRuntime)...")
            runtime = EnclaveRuntime(self.node_id)
        else:
            logger.info(f"Executing inference for messages via Local Runtime...")
            import os
            runtime = VLLMRuntime() if os.getenv("USE_VLLM") == "true" else SimulatedRuntime(self.node_id)
        
        start_time = time.time()
        ttft_ms = 0
        first_token = True
        tokens_generated = 0
        
        try:
            messages = job.get('messages', [])
            max_tokens = job.get('parameters', {}).get('max_tokens', 100)
            
            for chunk in runtime.execute(model_name, messages, max_tokens):
                if first_token:
                    ttft_ms = int((time.time() - start_time) * 1000)
                    first_token = False
                    
                headers = {}
                if NODE_AUTH_TOKEN:
                    headers["Authorization"] = f"Bearer {NODE_AUTH_TOKEN}"
                    
                requests.post(f"{CONTROL_PLANE_URL}/jobs/{job['id']}/chunk", json={"node_id": self.node_id, "chunk": chunk}, headers=headers)
                tokens_generated += 1
                
        except Exception as e:
            logger.error(f"Failed to stream chunk: {e}")
            
        logger.info(f"Inference completed. TTFT: {ttft_ms}ms. Streamed {tokens_generated} tokens.")
        
        # Report completion
        try:
            payload = {
                "node_id": self.node_id,
                "result_logs": f"Runtime output for model {model_name}. Tokens: {tokens_generated}",
                "tokens_generated": tokens_generated,
                "ttft_ms": ttft_ms
            }
            headers = {}
            if NODE_AUTH_TOKEN:
                headers["Authorization"] = f"Bearer {NODE_AUTH_TOKEN}"
                
            resp = requests.post(f"{CONTROL_PLANE_URL}/jobs/{job['id']}/complete", json=payload, headers=headers)
            resp.raise_for_status()
            logger.info(f"Successfully reported job {job['id']} completion to Control Plane.")
        except Exception as e:
            logger.error(f"Failed to report job completion: {e}")

    def run(self):
        self.register()
        self.is_running = True
        
        self.start_telemetry()
        
        poll_interval = 3
        last_poll = time.time()
        
        logger.info("Node Agent running...")
        while self.is_running:
            now = time.time()
            if now - last_poll > poll_interval:
                self.poll_for_jobs()
                last_poll = now
                
            time.sleep(1)
            
    def stop(self):
        logger.info("Stopping Node Agent...")
        self.is_running = False

if __name__ == "__main__":
    agent = NodeAgent()
    try:
        agent.run()
    except KeyboardInterrupt:
        agent.stop()

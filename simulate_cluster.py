import subprocess
import time
import sys
import requests
import os

CONTROL_PLANE_PORT = 8000
CONTROL_PLANE_URL = f"http://127.0.0.1:{CONTROL_PLANE_PORT}"

def wait_for_api():
    print("Waiting for Control Plane API to start...")
    for _ in range(30):
        try:
            resp = requests.get(f"{CONTROL_PLANE_URL}/nodes")
            if resp.status_code == 200:
                print("Control Plane is up!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    return False

def main():
    print("Starting AI Compute Network Local Simulation...")
    
    # Needs to be run from project root ideally
    os.environ["PYTHONPATH"] = "."
    
    # Reset DB
    if os.path.exists("compute_network.db"):
        os.remove("compute_network.db")
    
    # 1. Start Control Plane
    env = os.environ.copy()
    env["REDIS_URL"] = "redis://127.0.0.1:6379/0"
    env["NATS_URL"] = "nats://127.0.0.1:4222"
    
    control_plane_cmd = [sys.executable, "-m", "uvicorn", "control_plane.api.main:app", "--host", "127.0.0.1", "--port", str(CONTROL_PLANE_PORT)]
    print(f"Starting Control Plane: {' '.join(control_plane_cmd)}")
    cp_proc = subprocess.Popen(control_plane_cmd, env=env, stdout=sys.stdout, stderr=sys.stderr)
    
    if not wait_for_api():
        print("Failed to start API. Exiting.")
        cp_proc.terminate()
        sys.exit(1)
        
    node_procs = []
    try:
        # 2. Start 5 Node Agents
        # We need them to not conflict on the dashboard port (8080).
        # To do this correctly we'd inject port config, but for simulation we can just let one fail or disable dashboard config on others.
        # Since uvicorn in node agent hardcodes 8080 right now, 4 will fail to start dashboard but keep running agent.
        for i in range(5):
            env = os.environ.copy()
            env["REDIS_URL"] = "redis://127.0.0.1:6379/0"
            env["NATS_URL"] = "nats://127.0.0.1:4222"
            
            if i == 0:
                print("Starting Cloud-Burst Node (8x H100 Cluster)...")
                env["CLOUD_NODE"] = "1"
            else:
                print(f"Starting Decentralized Node Agent {i}...")
                
            np = subprocess.Popen([sys.executable, "-m", "node_agent.agent.core"], env=env, stdout=sys.stdout, stderr=sys.stderr)
            node_procs.append(np)
            time.sleep(1) # stagger registration
            
        print("Wait a few seconds for registration...")
        time.sleep(5)
        
        # 3. Submit Test Jobs via OpenAI compatible endpoint
        print("\n--- Submitting OpenAI Compatible Streaming Jobs ---")
        jobs_to_run = [
            {"model": "mistral-7b", "messages": [{"role": "user", "content": "Explain distributed systems vs decentralized networks."}], "stream": True, "max_tokens": 250},
            {"model": "llama-3-8b", "messages": [{"role": "user", "content": "Write a python script for a neural network."}], "stream": True, "max_tokens": 500},
        ]
        
        for j in jobs_to_run:
            try:
                headers = {"Authorization": "Bearer sk-admin"}
                with requests.post(f"{CONTROL_PLANE_URL}/v1/chat/completions", json=j, headers=headers, stream=True) as resp:
                    print("Stream Output: ", end="", flush=True)
                    for line in resp.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith("data: "):
                                data_str = line_str[6:]
                                if data_str == "[DONE]":
                                    print("\n[Stream Completed]")
                                    break
                                else:
                                    import json
                                    try:
                                        chunk_data = json.loads(data_str)
                                        content = chunk_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                        print(content, end="", flush=True)
                                    except:
                                        pass
            except Exception as e:
                print(f"Request failed: {e}")
            time.sleep(2) # brief pause before next job
            
        # 4. Wait for Auditor Agent to verify nodes
        print("\nWaiting 20 seconds for the Auditor Agent to test the nodes...")
        time.sleep(20)

        # 5. Check Nodes Earnings and Reputation
        print("\n--- Checking Node Status ---")
        resp = requests.get(f"{CONTROL_PLANE_URL}/nodes")
        if resp.status_code == 200:
            nodes = resp.json()
            for n in nodes:
                nid = n["id"]
                rep = n.get("reputation", 100)
                w_resp = requests.get(f"{CONTROL_PLANE_URL}/nodes/{nid}/wallet")
                if w_resp.status_code == 200:
                    w = w_resp.json()
                    print(f"Node {nid[:8]}... | Earned: ${w['pending_rewards']:.2f} | Reputation: {rep}/100")

    finally:
        print("\nShutting down cluster...")
        for p in node_procs:
            p.terminate()
        cp_proc.terminate()
        print("Done.")

if __name__ == "__main__":
    main()

import time
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("1. Registering Mock Developer Account...")
try:
    resp = requests.post(f"{BASE_URL}/auth/signup", json={"email": "test2@averra.com", "password": "pass"})
    api_key = resp.json().get("api_key")
except:
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "test2@averra.com", "password": "pass"})
    api_key = resp.json().get("api_key")

print("Developer API Key:", api_key)

print("\n2. Sending Non-Streaming Request for simpler parsing...")
headers = {"Authorization": f"Bearer {api_key}"}
payload = {
    "model": "mistral-7b",
    "messages": [{"role": "user", "content": "Tell me a joke."}],
    "stream": False,
    "max_tokens": 50
}

# Actually the API only supports streaming right now. So let's just trigger it and wait 5s.
payload["stream"] = True

try:
    requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, headers=headers)
    print("Inference triggered. Waiting for nodes to process...")
    time.sleep(5)
except Exception as e:
    print(e)
            
print("\n3. Checking Job Assignment & Wallet via control plane...")
jobs = requests.get(f"{BASE_URL}/jobs").json()
nodes = requests.get(f"{BASE_URL}/nodes").json()

print("Nodes:")
for n in nodes:
    print(n)
    wal = requests.get(f"{BASE_URL}/nodes/{n['id']}/wallet").json()
    print("  Wallet:", wal)

print("\nJobs:")
for j in jobs:
    print(j)

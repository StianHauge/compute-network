# Averra Node Agent

The Node Agent connects your hardware to the Averra inference network. It polls for jobs, executes inference, and streams results back to the Control Plane.

---

## Quick Start

### macOS / Linux (Headless)

```bash
# 1. Clone and install dependencies
git clone https://github.com/yourorg/averra.git
cd averra
pip install -r requirements.txt

# 2. Set your credentials
export CONTROL_PLANE_URL="https://averra.network"
export NODE_AUTH_TOKEN="averra_dev_secret_override_this"
export NODE_LINK_KEY="nk-av-your-key-from-dashboard"   # from averra.network/dashboard

# 3. Start the node
python -m node_agent.agent.core
```

> Get your `NODE_LINK_KEY` from [averra.network/dashboard](https://averra.network/dashboard) → Developer Nexus → Node Link Key

---

### macOS (Menu Bar App)

Download and install [Averra-Node-Installer.dmg](https://averra.network/downloads/Averra-Node-Installer-v1.0.3.dmg).

On first launch, you will be prompted to enter your Node Link Key. You can update it anytime via the menu bar icon → **Set Node Link Key...**

---

### Windows (System Tray App)

Download and run [Averra-Node-Installer.exe](https://averra.network/downloads/Averra-Node-Installer.exe).

Right-click the system tray icon → **Set Node Link Key...** to link your node to your account.

---

### CURL / One-liner Install (Linux)

```bash
curl -sSL https://install.averra.network | sh -s -- --token YOUR_NODE_LINK_KEY
```

Or manually with environment variables:

```bash
CONTROL_PLANE_URL=https://averra.network \
NODE_AUTH_TOKEN=averra_dev_secret_override_this \
NODE_LINK_KEY=nk-av-your-key \
python -m node_agent.agent.core
```

---

### CUDA / vLLM (GPU nodes)

For GPU nodes with a real vLLM backend:

```bash
export USE_VLLM=true
export CONTROL_PLANE_URL=https://averra.network
export NODE_AUTH_TOKEN=averra_dev_secret_override_this
export NODE_LINK_KEY=nk-av-your-key
python -m node_agent.agent.core
```

The agent will automatically spin up a vLLM Docker container for the requested model.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `CONTROL_PLANE_URL` | `https://averra.network` | Control Plane endpoint |
| `NODE_AUTH_TOKEN` | `averra_dev_secret_override_this` | Network authentication token |
| `NODE_LINK_KEY` | *(empty)* | Links node to your dashboard account |
| `NODE_LOCATION` | `local-machine` | Geographic label shown in Explorer |
| `NODE_TYPE` | `community` | `community` or `internal` |
| `USE_VLLM` | `false` | Set to `true` to use real vLLM Docker runtime |
| `CLOUD_NODE` | `0` | Set to `1` to report as cloud/H100 node |

---

## How It Works

1. **Register** — On startup, the agent registers hardware specs (CPU, GPU, VRAM) with the Control Plane via `POST /nodes/register`
2. **Telemetry** — Streams live GPU stats (temp, VRAM, PCIe) over WebSocket every second
3. **Poll** — Every 3 seconds, polls `POST /nodes/jobs/poll` for assigned inference jobs
4. **Execute** — Runs inference via `SimulatedRuntime` (default) or `VLLMRuntime` (GPU)
5. **Stream** — Pushes token chunks to `POST /jobs/{id}/chunk`, which publishes to Redis Pub/Sub
6. **Complete** — Reports job completion and triggers reward calculation

## Node Dashboard

View your node's earnings, status, and link key at [averra.network/dashboard](https://averra.network/dashboard).

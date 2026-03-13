#!/bin/bash
set -e

echo "==============================================="
echo "   Averra AI Compute Node - Linux Installer    "
echo "==============================================="

# 1. Require root or sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run this installer as root (e.g., sudo ./install-linux.sh)"
  exit 1
fi

NODE_DIR="/opt/averranode"
VENV_DIR="$NODE_DIR/venv"

# 2. Update and Install Dependencies
echo "[1/4] Installing system dependencies..."
apt-get update -y
apt-get install -y python3 python3-venv python3-pip git curl pciutils lshw

# 3. Create install directory
echo "[2/4] Setting up node directory at $NODE_DIR..."
mkdir -p "$NODE_DIR"
cd "$NODE_DIR" || exit

# 4. Clone or pull repo (In production, this downloads the latest release tarball)
# For this script we assume it's pulling from a git repo:
if [ ! -d "$NODE_DIR/.git" ]; then
    echo "This is a placeholder for downloading the actual Python source..."
    # git clone https://github.com/averra-network/node-agent.git .
    
    # We'll just create a dummy core.py file for testing the service
    mkdir -p node_agent/agent
    cat << 'EOF' > node_agent/agent/core.py
if __name__ == "__main__":
    import time
    print("Averra Node Agent running in Headless CLI mode...")
    while True:
        time.sleep(10)
EOF
fi

# 5. Setup Virtual Environment
echo "[3/4] Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# In production, we'd install requirements.txt here:
# pip install -r requirements.txt
pip install requests pydantic starlette fastapi uvicorn anyio

# 6. Create Systemd Service for persistence
echo "[4/4] Configuring Systemd Service for auto-restart on boot..."
SERVICE_FILE="/etc/systemd/system/averranode.service"

cat << EOF > "$SERVICE_FILE"
[Unit]
Description=Averra AI Decentralized Inference Node
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$NODE_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="CLOUD_NODE=0"
ExecStart=$VENV_DIR/bin/python -m node_agent.agent.core
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload and Enable Service
systemctl daemon-reload
systemctl enable averranode
systemctl start averranode

echo "==============================================="
echo " Installation Complete! 🚀"
echo " The Node Agent is now running in the background."
echo " Manage the service with:"
echo "   sudo systemctl status averranode"
echo "   sudo systemctl stop averranode"
echo "   sudo journalctl -u averranode -f (To view live logs)"
echo "==============================================="

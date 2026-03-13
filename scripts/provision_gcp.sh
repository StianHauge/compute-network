#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Configuration variables
PROJECT_ID="averra-490018"
PROJECT_NAME="Averra Network Production"
REGION="europe-west4"
ZONE="europe-west4-a"
INSTANCE_NAME="averra-control-plane"
MACHINE_TYPE="e2-medium"

echo "====================================================="
echo "🚀 Averra Network - GCP Infrastructure Provisioning"
echo "====================================================="

echo "[4/6] Enabling Compute Engine API (this may take a minute)..."

echo "[4/6] Enabling Compute Engine API (this may take a minute)..."
gcloud services enable compute.googleapis.com

echo "[5/6] Creating firewall rules for HTTP/HTTPS..."
gcloud compute firewall-rules create allow-http-https \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:80,tcp:443,tcp:8000 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=web-server || echo "Firewall rule already exists, ignoring."

echo "[6/6] Provisioning Ubuntu VM Instance: $INSTANCE_NAME..."
gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --tags=web-server \
    --metadata=startup-script="#! /bin/bash
        apt-get update
        apt-get install -y apt-transport-https ca-certificates curl software-properties-common git
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        add-apt-repository \"deb [arch=amd64] https://download.docker.com/linux/ubuntu \$(lsb_release -cs) stable\"
        apt-get update
        apt-get install -y docker-ce docker-compose
        systemctl enable docker
        systemctl start docker
        usermod -aG docker ubuntu
        
        # Clone repository
        cd /home/ubuntu
        git clone https://github.com/stianhauge/compute-network.git # Replace with actual repo URL if private
        cd compute-network
        
        # Deploy
        chmod +x scripts/deploy_gcp.sh
        ./scripts/deploy_gcp.sh
    "

echo "====================================================="
echo "✅ Provisioning initiated successfully!"
echo "The server is booting up and installing Docker in the background."
echo "To get the public IP address, run:"
echo "gcloud compute instances list --project=$PROJECT_ID"
echo "====================================================="

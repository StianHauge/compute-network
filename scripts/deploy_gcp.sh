#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting deployment sequence for Averra Network..."

echo "1. Pulling latest code from Git..."
git pull origin main

echo "2. Rebuilding and restarting Docker containers..."
sudo docker-compose down
sudo docker-compose build --no-cache
sudo docker-compose up -d

echo "Deployment complete! Here are the running containers:"
sudo docker-compose ps

echo "Checking logs for API..."
sudo docker-compose logs --tail=20 api

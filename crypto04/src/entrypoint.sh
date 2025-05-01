#!/bin/bash

#rm -f /var/run/docker.pid
#rm -f /var/run/containerd/containerd.pid
#dockerd &

# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
export PATH="$HOME/.foundry/bin:$PATH"
echo "CIAOOOO"
~/.foundry/bin/foundryup

# 🧠 Wait for Docker daemon
#until docker info &>/dev/null; do
#  echo "Waiting for Docker daemon..."
#  sleep 1
#done
#echo "Docker daemon is up"

#docker pull ghcr.io/foundry-rs/foundry

#docker build -t offchain-signer /app/offchain

#docker network create orchestrator-net

# Start your orchestrator
echo "DONE"
python3 /app/orchestrator.py # > /tmp/orchestrator.log 2>&1 &

sleep infinity


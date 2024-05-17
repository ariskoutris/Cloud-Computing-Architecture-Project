#!/bin/bash

SERVER_THREADS=$1
SERVER_CORES=$2

# VM Names
SERVER_VM="$(kubectl get nodes -o wide | awk '/memcache-server/ {print $1}')"
AGENT_VM="$(kubectl get nodes -o wide | awk '/client-agent/ {print $1}')"
CLIENT_VM="$(kubectl get nodes -o wide | awk '/client-measure/ {print $1}')"

# Server Configuration
CONFIG_FILE="/etc/memcached.conf"
SERVER_MEMORY=1024
SERVER_IP="$(kubectl get nodes -o wide | awk '/memcache-server/ {print $6}')"
SERVER_SETUP="
    sudo apt-get update
    sudo apt-get purge -y memcached libmemcached-tools && sudo apt-get install -y memcached libmemcached-tools
    sudo systemctl status memcached
    sudo sed -i '/^-m /c\-m $SERVER_MEMORY' $CONFIG_FILE
    sudo sed -i '/^-l /c\-l $SERVER_IP' $CONFIG_FILE
    sudo systemctl restart memcached
    sudo systemctl status memcached
"

echo "Setting up memcached server on $SERVER_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$SERVER_VM" --zone europe-west3-a --command "$SERVER_SETUP"
echo "Please make sure that the server is running here, or cancel the script if it is not."
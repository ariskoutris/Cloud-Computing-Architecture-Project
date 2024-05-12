#!/bin/bash

# VM Names
SERVER_VM="$(kubectl get nodes -o wide | awk '/memcache-server/ {print $1}')"
AGENT_VM="$(kubectl get nodes -o wide | awk '/client-agent/ {print $1}')"
CLIENT_VM="$(kubectl get nodes -o wide | awk '/client-measure/ {print $1}')"

# Server Configuration
CONFIG_FILE="/etc/memcached.conf"
SERVER_MEMORY=1024
SERVER_THREADS=16
SERVER_IP="$(kubectl get nodes -o wide | awk '/memcache-server/ {print $6}')"
SERVER_SETUP="
    sudo apt-get update
    sudo apt-get purge -y memcached libmemcached-tools && sudo apt-get install -y memcached libmemcached-tools
    sudo systemctl status memcached
    sudo sed -i '/^-m /c\-m $SERVER_MEMORY' $CONFIG_FILE
    sudo sed -i '/^-l /c\-l $SERVER_IP' $CONFIG_FILE
    echo '-t $SERVER_THREADS' | sudo tee -a $CONFIG_FILE > /dev/null
    sudo systemctl restart memcached
    sleep 1
    sudo systemctl status memcached
"
# VM setup
MCPERF_SETUP="
    sudo sh -c 'echo deb-src http://europe-west3.gce.archive.ubuntu.com/ubuntu/ jammy main restricted >> /etc/apt/sources.list'
    sudo apt-get update
    sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes
    sudo apt-get build-dep memcached --yes
    git clone https://github.com/eth-easl/memcache-perf-dynamic.git
    cd memcache-perf-dynamic
    make
"

echo "Setting up memcached server on $SERVER_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$SERVER_VM" --zone europe-west3-a --command "$SERVER_SETUP"
echo "Please make sure that the server is running here, or cancel the script if it is not."
sleep 5
echo "Setting up mcperf on $AGENT_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$AGENT_VM" --zone europe-west3-a --command "$MCPERF_SETUP"
echo "Setting up mcperf on $CLIENT_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$CLIENT_VM" --zone europe-west3-a --command "$MCPERF_SETUP"

echo "Setup complete."
printf "Note, to bind memcached to specific CPUs, use:\n\t$ taskset -p 0-1 \$(pgrep memcached)"

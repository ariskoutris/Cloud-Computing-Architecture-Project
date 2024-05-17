#!/bin/bash

# VM Names
SERVER_VM="$(kubectl get nodes -o wide | awk '/memcache-server/ {print $1}')"
AGENT_VM="$(kubectl get nodes -o wide | awk '/client-agent/ {print $1}')"
CLIENT_VM="$(kubectl get nodes -o wide | awk '/client-measure/ {print $1}')"

# Server Configuration
CONFIG_FILE="/etc/memcached.conf"
SERVER_MEMORY=1024
SERVER_THREADS=2
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

# Adapted from https://docs.docker.com/engine/install/ubuntu/
DOCKER_SETUP="
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo docker pull anakli/cca:parsec_blackscholes
    sudo docker pull anakli/cca:parsec_canneal
    sudo docker pull anakli/cca:parsec_dedup
    sudo docker pull anakli/cca:parsec_ferret
    sudo docker pull anakli/cca:parsec_freqmine
    sudo docker pull anakli/cca:splash2x_radix
"

PYTHON_SETUP="
    sudo apt-get update
    sudo apt install python3-pip --yes
    pip3 install psutil docker
    sudo usermod -a -G docker ubuntu
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

echo "Setting up docker on $SERVER_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$SERVER_VM" --zone europe-west3-a --command "$DOCKER_SETUP"
echo "Setting up python on $SERVER_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$SERVER_VM" --zone europe-west3-a --command "$PYTHON_SETUP"
echo "Setting up memcached server on $SERVER_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$SERVER_VM" --zone europe-west3-a --command "$SERVER_SETUP"
echo "Please make sure that the server is running here, or cancel the script if it is not."
sleep 5
echo "Sending scheduler scheduler to $SERVER_VM..."
gcloud compute scp -r --ssh-key-file ~/.ssh/cloud-computing scheduler ubuntu@"$SERVER_VM":~/ --zone europe-west3-a
echo "Setting up mcperf on $AGENT_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$AGENT_VM" --zone europe-west3-a --command "$MCPERF_SETUP"
echo "Setting up mcperf on $CLIENT_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$CLIENT_VM" --zone europe-west3-a --command "$MCPERF_SETUP"


echo "Setup complete."


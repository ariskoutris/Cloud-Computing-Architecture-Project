#!/bin/bash

# Set up memcached
echo "Creating memcached pod..."
kubectl create -f memcache-t1-cpuset.yaml

echo "Exposing memcached pod..."
kubectl expose pod some-memcached --name some-memcached-11211 --type LoadBalancer --port 11211 --protocol TCP

echo "Waiting for 60 seconds for the service to be up and running..."
sleep 60

echo "Getting service details..."
kubectl get service some-memcached-11211

echo "Confirming that the memcached service is running..."
kubectl get pods -o wide

# VM Names
AGENT_VM_A=${("$(kubectl get nodes -o wide | awk '/client-agent-a/ {print $1}')")[0]}
AGENT_VM_B=${("$(kubectl get nodes -o wide | awk '/client-agent-b/ {print $1}')")[0]}
CLIENT_VM=${("$(kubectl get nodes -o wide | awk '/client-measure/ {print $1}')")[0]}

# Commands to run on each VM
SSH_COMMANDS="
sudo sh -c "echo deb-src http://europe-west3.gce.archive.ubuntu.com/ubuntu/ jammy main restricted >> /etc/apt/sources.list"
sudo apt-get update
sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes
sudo apt-get build-dep memcached --yes
git clone https://github.com/eth-easl/memcache-perf-dynamic.git
cd memcache-perf-dynamic
make
"


echo "Setting up mcperf on $AGENT_VM_A..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$AGENT_VM_A" --zone europe-west3-a --command "$SSH_COMMANDS"
echo "Setting up mcperf on $AGENT_VM_B..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$AGENT_VM_B" --zone europe-west3-a --command "$SSH_COMMANDS"
echo "Setting up mcperf on $CLIENT_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$CLIENT_VM" --zone europe-west3-a --command "$SSH_COMMANDS"

echo "Setup complete."

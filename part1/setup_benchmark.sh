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
AGENT_VM=("$(kubectl get nodes -o wide | awk '/client-agent/ {print $1}')")
CLIENT_VM=("$(kubectl get nodes -o wide | awk '/client-measure/ {print $1}')")

# Commands to run on each VM
SSH_COMMANDS="
sudo apt-get update
sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes
sudo cp /etc/apt/sources.list /etc/apt/sources.list~
sudo sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list
sudo apt-get update
sudo apt-get build-dep memcached --yes
cd && git clone https://github.com/shaygalon/memcache-perf.git
cd memcache-perf
git checkout 0afbe9b
make
"


echo "Setting up mcperf on $AGENT_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$AGENT_VM" --zone europe-west3-a --command "$SSH_COMMANDS"
echo "Setting up mcperf on $CLIENT_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$CLIENT_VM" --zone europe-west3-a --command "$SSH_COMMANDS"

echo "Setup complete."

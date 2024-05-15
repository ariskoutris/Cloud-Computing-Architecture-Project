#!/bin/bash

SERVER_THREADS=$1
SERVER_CORES=$2

# VM Names
AGENT_VM=$(kubectl get nodes -o wide | awk '/client-agent/ {print $1}')
CLIENT_VM=$(kubectl get nodes -o wide | awk '/client-measure/ {print $1}')

# VM IPs
INTERNAL_AGENT_IP=$(kubectl get nodes -o wide | awk '/client-agent/ {print $6}')
INTERNAL_CLIENT_VM=$(kubectl get nodes -o wide | awk '/memcache-server/ {print $6}')

OUTPUT_FILE="memcached_results_T=$SERVER_THREADS,C=$SERVER_CORES.txt"

CLIENT_AGENT_COMMANDS="pkill mcperf && ./memcache-perf-dynamic/mcperf -T 16 -A"

CLIENT_MEASURE_COMMANDS="
  pkill mcperf
  touch ~/memcache-perf-dynamic/$OUTPUT_FILE
  ./memcache-perf-dynamic/mcperf -s $INTERNAL_CLIENT_VM --loadonly
  ./memcache-perf-dynamic/mcperf -s $INTERNAL_CLIENT_VM -a $INTERNAL_AGENT_IP --noload -T 16 -C 4 -D 4 -Q 1000 -c 4 -t 5 --scan 5000:125000:5000 >> $OUTPUT_FILE
"

# Run command on CLIENT_AGENT VM
echo "Launching mcperf client load agent on $AGENT_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$AGENT_VM" --zone europe-west3-a --command "$CLIENT_AGENT_COMMANDS" &
sleep 5

# Run commands on CLIENT_VM
echo "Running measurements on $CLIENT_VM..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$CLIENT_VM" --zone europe-west3-a --command "$CLIENT_MEASURE_COMMANDS"

echo "Downloading results from $CLIENT_VM..."
gcloud compute scp ubuntu@"$CLIENT_VM":~/$OUTPUT_FILE ./results/ --zone europe-west3-a --ssh-key-file ~/.ssh/cloud-computing
echo "Results downloaded."

#!/bin/bash

# Extract INTERNAL_AGENT_IP
INTERNAL_AGENT_A_IP=$(kubectl get nodes -o wide | awk '/client-agent-a/ {print $6}')
INTERNAL_AGENT_B_IP=$(kubectl get nodes -o wide | awk '/client-agent-b/ {print $6}')

# VM Names
AGENT_VM_A="$(kubectl get nodes -o wide | awk '/client-agent-a/ {print $1}')"
AGENT_VM_B="$(kubectl get nodes -o wide | awk '/client-agent-b/ {print $1}')"
CLIENT_MEASURE="$(kubectl get nodes -o wide | awk '/client-measure/ {print $1}')"

# Commands to run on CLIENT_AGENT VM
# Note: Use nohup to run the command in the background and redirect the output to /dev/null
CLIENT_AGENT_A_COMMANDS="pkill mcperf && ./memcache-perf-dynamic/mcperf -T 2 -A >> /dev/null"
CLIENT_AGENT_B_COMMANDS="pkill mcperf && ./memcache-perf-dynamic/mcperf -T 4 -A >> /dev/null"

# Extract MEMCACHED_IP
MEMCACHED_IP=$(kubectl get pods -o wide | awk '/some-memcached/ {print $6}')

OUTPUT_FILE="memcached_results_1.txt"

# Run command on CLIENT_AGENT VM
echo "Launching mcperf client load agent on $AGENT_VM_A..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$AGENT_VM_A" --zone europe-west3-a --command "$CLIENT_AGENT_A_COMMANDS" &
sleep 3
echo "Launching mcperf client load agent on $AGENT_VM_B..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$AGENT_VM_B" --zone europe-west3-a --command "$CLIENT_AGENT_B_COMMANDS" &
sleep 3

CLIENT_MEASURE_COMMANDS="
  pkill mcperf
  touch ~/memcache-perf-dynamic/$OUTPUT_FILE
  ./memcache-perf-dynamic/mcperf -s $MEMCACHED_IP --loadonly
  ./memcache-perf-dynamic/mcperf -s $MEMCACHED_IP -a $INTERNAL_AGENT_B_IP -a $INTERNAL_AGENT_A_IP --noload -T 6 -C 4 -D 4 -Q 1000 -c 4 -t 10 --scan 30000:30500:5 >> $OUTPUT_FILE
"

# Run commands on CLIENT_MEASURE VM
echo "Running measurements on $CLIENT_MEASURE..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$CLIENT_MEASURE" --zone europe-west3-a --command "$CLIENT_MEASURE_COMMANDS" &
# Make sure memcached is running
sleep 10


# Run the PARSEC jobs script
echo "Running the PARSEC jobs script..."
./run_parsec_revised.sh

echo "Downloading results from $CLIENT_MEASURE..."
gcloud compute scp ubuntu@"$CLIENT_MEASURE":~/$OUTPUT_FILE ./results/ --zone europe-west3-a --ssh-key-file ~/.ssh/cloud-computing
echo "Results downloaded."

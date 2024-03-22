#!/bin/bash

# Extract INTERNAL_AGENT_IP
INTERNAL_AGENT_IP=$(kubectl get nodes -o wide | awk '/client-agent/ {print $6}')

# VM Names
CLIENT_AGENT=("$(kubectl get nodes -o wide | awk '/client-agent/ {print $1}')")
CLIENT_MEASURE=("$(kubectl get nodes -o wide | awk '/client-measure/ {print $1}')")

# Commands to run on CLIENT_AGENT VM
# Note: Use nohup to run the command in the background and redirect the output to /dev/null
CLIENT_AGENT_COMMANDS="nohup ./memcache-perf/mcperf -T 16 -A > /dev/null 2>&1 & echo \$! > mcperf.pid"

# Extract MEMCACHED_IP
MEMCACHED_IP=$(kubectl get pods -o wide | awk '/some-memcached/ {print $6}')

# Run command on CLIENT_AGENT VM
echo "Launching mcperf client load agent on $CLIENT_AGENT..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@$CLIENT_AGENT --zone europe-west3-a --command "$CLIENT_AGENT_COMMANDS"
sleep 30

for BENCHMARK in "some-memcached" "ibench-cpu" "ibench-l1d" "ibench-l1i" "ibench-l2" "ibench-llc" "ibench-membw"; do

  # Output file name
  OUTPUT_FILE="$BENCHMARK.txt"

  # Commands to run on CLIENT_MEASURE VM
  # Note: Using single quotes to delay variable expansion until executed on the remote machine
  CLIENT_MEASURE_COMMANDS="
  touch ~/memcache-perf/$OUTPUT_FILE
  ./memcache-perf/mcperf -s $MEMCACHED_IP --loadonly
  for i in {1..3}; do
      ./memcache-perf/mcperf -s $MEMCACHED_IP -a $INTERNAL_AGENT_IP --noload -T 16 -C 4 -D 4 -Q 1000 -c 4 -t 5 -w 2 --scan 5000:55000:5000 >> $OUTPUT_FILE
  done
  "

  echo "---------------------$BENCHMARK---------------------"

  if [ "$BENCHMARK" != "some-memcached" ]; then
    echo "Creating interference pod for $BENCHMARK..."
    kubectl create -f interference/$BENCHMARK.yaml
    echo "Wait for 60 seconds for the interference pod to be up and running..."
    sleep 60
    kubectl get pods -o wide
  fi

  # Run commands on CLIENT_MEASURE VM
  echo "Running benchmarks on $CLIENT_MEASURE..."
  gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@"$CLIENT_MEASURE" --zone europe-west3-a --command "$CLIENT_MEASURE_COMMANDS"
  echo "Benchmark complete."

  echo "Downloading results from $CLIENT_MEASURE..."
  gcloud compute scp ubuntu@"$CLIENT_MEASURE":~/$OUTPUT_FILE ./results/ --zone europe-west3-a --ssh-key-file ~/.ssh/cloud-computing
  echo "Results downloaded."

{
    # Print the header with an extra column for the iteration number
    echo "run_id,type,avg,std,min,p5,p10,p50,p67,p75,p80,p85,p90,p95,p99,p999,p9999,QPS,target"

    # Process the file
    awk '
    BEGIN {
        run_id = 1
    }
    /CPU Usage Stats/ {
        run_id++
        next
    }
    /^read/ {
        # Replace multiple spaces with a single comma for CSV format
        gsub(/ +/, ",")
        print run_id "," $0
    }' "results/$OUTPUT_FILE"
} > "results/$BENCHMARK.csv"

  if [ "$BENCHMARK" != "some-memcached" ]; then
    echo "Removing interference pod for $BENCHMARK..."
    kubectl delete pods $BENCHMARK
  fi
done

echo "Terminating mcperf client load agent on $CLIENT_AGENT..."
gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@$CLIENT_AGENT --zone europe-west3-a --command "kill \$(cat mcperf.pid) && rm mcperf.pid"
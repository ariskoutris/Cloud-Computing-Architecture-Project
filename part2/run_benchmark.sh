#!/bin/bash

# Array of PARSEC Jobs
PARSEC_JOBS=("parsec-blackscholes" "parsec-canneal" "parsec-dedup" "parsec-ferret" "parsec-freqmine" "parsec-radix" "parsec-vips")

# Array of Sources of Interference (IBENCH_SOI) Benchmarks
SOI_BENCHMARKS=("ibench-cpu" "ibench-l1d" "ibench-l1i" "ibench-l2" "ibench-llc" "ibench-membw")

# Loop through each PARSEC job
for PARSEC_JOB in "${PARSEC_JOBS[@]}"; do
    for IBENCH_SOI in "${SOI_BENCHMARKS[@]}"; do

        echo "Creating interference pod for $IBENCH_SOI..."
        kubectl create -f interference/$IBENCH_SOI.yaml
        echo "Wait for 60 seconds for the interference pod to be up and running..."
        sleep 60
        kubectl get pods -o wide

        echo "Deploying PARSEC job $PARSEC_JOB..."
        kubectl create -f "parsec-benchmarks/part2a/${PARSEC_JOB}.yaml"
        
        echo "Waiting for job to complete..."
        while true; do
            CONDITION=$(kubectl get job $PARSEC_JOB -o jsonpath='{.status.conditions[0].type}')
            STATUS=$(kubectl get job $PARSEC_JOB -o jsonpath='{.status.conditions[0].status}')
            SUCCEEDED=$(kubectl get job $PARSEC_JOB -o jsonpath='{.status.succeeded}')
            if [[ "$CONDITION" == "Complete" && "$STATUS" == "True" && "$SUCCEEDED" == "1" ]]; then
                echo "Job $PARSEC_JOB has completed successfully."
                break
            else
                sleep 5
            fi
        done
        kubectl get jobs
        (kubectl logs $(kubectl get pods --selector=job-name=$PARSEC_JOB --output=jsonpath='{.items[*].metadata.name}')) > results/$PARSEC_JOB_$IBENCH_SOI.txt

        echo "Removing interference pod for $IBENCH_SOI..."
        kubectl delete pods $IBENCH_SOI

        echo "Removing PARSEC job $PARSEC_JOB..."
        kubectl delete job $PARSEC_JOB
        
    done
done

#!/bin/bash

# Array of PARSEC Jobs
PARSEC_JOBS=("parsec-blackscholes" "parsec-canneal" "parsec-dedup" "parsec-ferret" "parsec-freqmine" "parsec-radix" "parsec-vips")

# Array of Sources of Interference (IBENCH_SOI) Benchmarks
SOI_BENCHMARKS=("no-interference" "ibench-cpu" "ibench-l1d" "ibench-l1i" "ibench-l2" "ibench-llc" "ibench-membw")

for PARSEC_JOB in "${PARSEC_JOBS[@]}"; do
    for IBENCH_SOI in "${SOI_BENCHMARKS[@]}"; do

        if [ "$IBENCH_SOI" != "no-interference" ]; then
            echo "Creating interference pod for $IBENCH_SOI..."
            kubectl create -f interference/$IBENCH_SOI.yaml
            echo "Wait for 60 seconds for the interference pod to be up and running..."
            sleep 60
            kubectl get pods -o wide
        else
            echo "Running $PARSEC_JOB without interference..."
        fi

        echo "Deploying job $PARSEC_JOB..."
        kubectl create -f "parsec-benchmarks/part2a/${PARSEC_JOB}.yaml"
        
        echo "Waiting for job to complete..."
        while true; do
            JOB_CONDITION=$(kubectl get jobs $PARSEC_JOB -o jsonpath='{.status.conditions[0].type}')   
            if [ "$JOB_CONDITION" == "Complete" ]; then
                echo "Job $PARSEC_JOB has completed successfully."
                break
            elif [ "$JOB_CONDITION" == "Failed" ]; then
                echo "Job $PARSEC_JOB has failed."
                break
            else
                sleep 5
            fi
        done
        
        kubectl get jobs
        (kubectl logs $(kubectl get pods --selector=job-name=$PARSEC_JOB --output=jsonpath='{.items[*].metadata.name}')) > results/${PARSEC_JOB}_${IBENCH_SOI}.txt

        if [ "$IBENCH_SOI" != "no-interference" ]; then
            echo "Removing interference pod for $IBENCH_SOI..."
            kubectl delete pods $IBENCH_SOI
        fi

        echo "Removing job $PARSEC_JOB..."
        kubectl delete job $PARSEC_JOB
        
        echo "----------------------------------------"
    done
done

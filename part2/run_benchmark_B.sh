#!/bin/bash

PARSEC_JOBS=("parsec-blackscholes" "parsec-canneal" "parsec-dedup" "parsec-ferret" "parsec-freqmine" "parsec-radix" "parsec-vips")

for PARSEC_JOB in "${PARSEC_JOBS[@]}"; do
    TEMPLATE_FILE="parsec-benchmarks/part2b/${PARSEC_JOB}.yaml"
    
    for n_threads in 1 2 4 8; do
        echo "Deploying job $PARSEC_JOB with $n_threads threads..."
        sed "s/-n \${N_THREADS}/-n $n_threads/g" $TEMPLATE_FILE | kubectl create -f -
        
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
        (kubectl logs $(kubectl get pods --selector=job-name=$PARSEC_JOB --output=jsonpath='{.items[*].metadata.name}')) > results_B/${PARSEC_JOB}_${n_threads}.txt

        echo "Removing job $PARSEC_JOB..."
        kubectl delete job $PARSEC_JOB
        
        echo "----------------------------------------"
    done
done

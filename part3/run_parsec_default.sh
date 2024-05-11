#!/bin/bash

PARSEC_JOBS=("parsec-blackscholes" "parsec-canneal" "parsec-dedup" "parsec-ferret" "parsec-freqmine" "parsec-radix" "parsec-vips")
PARSEC_JOBS_1=("parsec-blackscholes" "parsec-vips" "parsec-freqmine")
PARSEC_JOBS_2=("parsec-canneal" "parsec-dedup" "parsec-ferret" "parsec-radix")

for PARSEC_JOB in "${PARSEC_JOBS_1[@]}"; do
    TEMPLATE_FILE="parsec-benchmarks/${PARSEC_JOB}.yaml"
    echo "Deploying job $PARSEC_JOB"
    kubectl create -f $TEMPLATE_FILE
done

vips_flag=true
freqmine_flag=true
while true; do
    all_jobs_complete=true
    for PARSEC_JOB in "${PARSEC_JOBS_1[@]}"; do
        JOB_CONDITION=$(kubectl get jobs $PARSEC_JOB -o jsonpath='{.status.conditions[0].type}')   
        if [ "$JOB_CONDITION" == "Complete" ]; then
            echo "Job $PARSEC_JOB has completed successfully."
            if [ "$PARSEC_JOB" == "parsec-vips" ] & $vips_flag; then
                echo "Deploying ferret and radix"
                kubectl create -f parsec-benchmarks/parsec-ferret.yaml
                kubectl create -f parsec-benchmarks/parsec-radix.yaml
                vips_flag=false
            elif [ "$PARSEC_JOB" == "parsec-freqmine" ] & $freqmine_flag; then
                echo "Deploying canneal and dedup"
                kubectl create -f parsec-benchmarks/parsec-canneal.yaml
                kubectl create -f parsec-benchmarks/parsec-dedup.yaml
                freqmine_flag=false
            fi
        elif [ "$JOB_CONDITION" == "Failed" ]; then
            echo "Job $PARSEC_JOB has failed."
            break
        else
            all_jobs_complete=false
        fi
    done
    if $all_jobs_complete; then
        break
    fi
    sleep 0.1
done

 while true; do
    all_jobs_complete=true
    for PARSEC_JOB in "${PARSEC_JOBS[@]}"; do
        JOB_CONDITION=$(kubectl get jobs $PARSEC_JOB -o jsonpath='{.status.conditions[0].type}')   
        if [ "$JOB_CONDITION" == "Complete" ]; then
            echo "Job $PARSEC_JOB has completed successfully."
        elif [ "$JOB_CONDITION" == "Failed" ]; then
            echo "Job $PARSEC_JOB has failed."
            break
        else
            all_jobs_complete=false
        fi
    done
    if $all_jobs_complete; then
        break
    fi
    sleep 0.1
done

for PARSEC_JOB in "${PARSEC_JOBS[@]}"; do
    echo "Getting logs for job $PARSEC_JOB"
    (kubectl logs $(kubectl get pods --selector=job-name=$PARSEC_JOB --output=jsonpath='{.items[*].metadata.name}')) > results/${PARSEC_JOB}.txt
done

kubectl get pods -o json > results_1/results.json
python3 get_time.py results_1/results.json

echo "Removing jobs and pods"
kubectl delete jobs --all
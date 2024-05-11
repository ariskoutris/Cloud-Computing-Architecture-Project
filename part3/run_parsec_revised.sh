#!/bin/bash

PARSEC_JOBS=("parsec-blackscholes" "parsec-canneal" "parsec-dedup" "parsec-ferret" "parsec-freqmine" "parsec-radix" "parsec-vips")

# Waits and checks if the job is complete
check_job_completion() {
    local job_name=$1
    while true; do
        JOB_CONDITION=$(kubectl get jobs $job_name -o jsonpath='{.status.conditions[0].type}')
        if [ "$JOB_CONDITION" == "Complete" ]; then
            echo "$job_name is complete."
            break
        fi
        sleep 3
    done
}

# Start the job
start_job() {
    local job_config=$1
    echo "Starting job $job_config..."
    kubectl create -f parsec-benchmarks/$job_config.yaml
}
# Runs first job and once complete starts the next jobs in parallel
sequential_run_jobs() {
    local job_name=$1
    local dependent_jobs=("${!2}")

    start_job $job_name
    check_job_completion $job_name

    for job in "${dependent_jobs[@]}"; do
        start_job $job
    done
}

ferret_dependent_jobs=()
freqmine_dependent_jobs=()
blackscholes_dependent_jobs=()
canneal_dependent_jobs=()
radix_dependent_jobs=("parsec-vips" "parsec-dedup")

# Node 2cores
sequential_run_jobs "parsec-blackscholes" blackscholes_dependent_jobs[@] &
# Node 4cores
sequential_run_jobs "parsec-ferret" ferret_dependent_jobs[@] &
sequential_run_jobs "parsec-canneal" canneal_dependent_jobs[@] &
# Node 8cores
start_job "parsec-freqmine"
check_job_completion "parsec-freqmine"
sequential_run_jobs "parsec-radix" radix_dependent_jobs[@] &


for PARSEC_JOB in "${PARSEC_JOBS[@]}"; do
    check_job_completion $PARSEC_JOB
done

echo "All jobs are finished."

kubectl get pods -o json > results/results.json
python3 get_time.py results/results.json

echo "Removing jobs and pods"
kubectl delete jobs --all
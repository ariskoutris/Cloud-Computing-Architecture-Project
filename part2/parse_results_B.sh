#!/bin/bash

# Directory containing the results
results_dir="results_B"

# Temporary file for holding intermediate results
temp_file="temp_results_B.csv"

# Clear the temp file to start fresh
> "$temp_file"

# Loop through all .txt files in the results_B directory
for file in "$results_dir"/*.txt; do
    # Extract benchmark name and number of threads from the filename
    filename=$(basename "$file")
    benchmark=$(echo "$filename" | sed -E 's/parsec-([a-zA-Z0-9]+)_.*/\1/')
    num_threads=$(echo "$file" | sed -E 's/.*_([0-9]+)\.txt/\1/')

    # Extract the execution time and convert it to seconds
    time_in_seconds=$(grep '^real' "$file" | awk '{print $2}' | awk -F'm' '{split($2,a,"s"); print ($1 * 60) + a[1]}')

    # Check for errors in time conversion
    if [ -z "$time_in_seconds" ]; then
        echo "Error processing file $file: Time conversion failed."
        continue
    fi

    # Write the results to a temporary file
    echo "$benchmark,$num_threads,$time_in_seconds" >> "$temp_file"
done

# Calculate speedup and generate CSV headers and data
awk -F',' '
{
    benchmarks[$1]
    threads[$2]
    times[$1","$2]=$3
    if ($2 == 1) {
        base_time[$1]=$3
    }
}
END {
    printf "Benchmark"
    for (t in threads) {
        printf ",%s", t
    }
    printf "\n"

    for (b in benchmarks) {
        printf "%s", b
        for (t in threads) {
            key=b","t
            if (times[key] > 0 && base_time[b] > 0) {
                printf ",%.2f", base_time[b] / times[key]
            } else {
                printf ","
            }
        }
        printf "\n"
    }
}' "$temp_file" > results_B.csv

# Clean up
rm "$temp_file"

echo "Results have been written to results_B.csv."

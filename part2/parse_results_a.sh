#!/bin/bash

# Directory containing the results
results_dir="results_A"

# Temporary file for holding intermediate results
temp_file="temp_results.csv"

# Clear the temp file to start fresh
> "$temp_file"

# Loop through all .txt files in the results_A directory
for file in "$results_dir"/*.txt; do
    # Extract benchmark name and interference type from the filename
    filename=$(basename "$file")
    benchmark=$(echo "$filename" | sed -E 's/parsec-([a-zA-Z0-9]+)_.*/\1/')
    interference=$(echo "$filename" | sed -E 's/.*_([a-zA-Z0-9-]+)\.txt/\1/')

    # Extract the execution time and convert it to seconds
    # Adjust the parsing logic to correctly extract minutes and seconds
    time_in_seconds=$(grep '^real' "$file" | awk '{print $2}' | awk -F'm' '{split($2,a,"s"); print ($1 * 60) + a[1]}')

    # Check for errors in time conversion
    if [ -z "$time_in_seconds" ]; then
        echo "Error processing file $filename: Time conversion failed."
        continue
    fi

    # Write the results to a temporary file
    echo "$benchmark,$interference,$time_in_seconds" >> "$temp_file"
done

# Generate CSV headers and data
awk -F',' '{
    benchmarks[$1]
    interferences[$2]
    times[$1","$2]=$3
    if ($2 == "no-interference") {
        base_time[$1]=$3
    }
}
END {
    printf "Benchmark"
    for (i in interferences) {
        printf ",%s", i
    }
    printf "\n"

    for (b in benchmarks) {
        printf "%s", b
        for (i in interferences) {
            printf ",%s", times[b","i] / base_time[b]
        }
        printf "\n"
    }
}' "$temp_file" > "results_A.csv"

# Clean up
rm "$temp_file"

echo "Results have been written to results_A.csv."

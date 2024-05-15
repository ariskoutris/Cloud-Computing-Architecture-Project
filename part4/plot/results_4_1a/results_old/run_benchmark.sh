#!/bin/bash
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
    }' "$OUTPUT_FILE"
} > "$out.csv"

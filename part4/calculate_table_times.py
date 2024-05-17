import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pytz
from datetime import datetime
from dateutil import parser
import json
import matplotlib.patches as mpatches
import statistics

utc=pytz.UTC
sns.set_theme()


benchmarks = ['dedup', 'vips', 'radix','freqmine', 'canneal', 'ferret', 'blackscholes' ]

def transform_date_string(str):
    time = datetime.strptime(str,"%Y-%m-%dT%H:%M:%S.%f")
    sec= time.hour*3600 + time.minute*60 + time.second
    return sec

def get_benchmark_times(data, benchmark):
    start_times = []
    end_times = []
    for index, row in data.iterrows():
        if benchmark == row['job']:
            if row['action'] == 'start' or row['action'] == 'unpause':
                start = row['timestamp']
                start_sec= transform_date_string(start)
                start_times.append(start_sec)
            if row['action']  == 'end' or row['action'] == 'pause':
                end = row['timestamp']
                end_sec= transform_date_string(end)
                end_times.append(end_sec)
    return start_times , end_times

def calculate():
    times = {name: [] for name in benchmarks}
    scheduler_times = []
    for i in range(3):
        jobs_path = f'part4/plot/results_4_4/jobs_{i}.txt'
        jobs = pd.read_csv(jobs_path, delim_whitespace=True)

        runtimes_start = {name: [] for name in benchmarks}
        runtimes_end = {name: [] for name in benchmarks}
        for name in benchmarks:
                runtimes_start[name], runtimes_end[name] = get_benchmark_times(jobs, name)
        
        for name in benchmarks:
            time = 0
            for k,s in enumerate(runtimes_start[name]):
                time += runtimes_end[name][k] - s
            times[name].append(time)

        
        for index, row in jobs.iterrows():
            if row['job'] == 'scheduler':
                if row['action'] == 'start':
                    start = row['timestamp']
                    start_sec= transform_date_string(start)
                if row['action']  == 'end':
                    end = row['timestamp']
                    end_sec= transform_date_string(end)
        schedule = end_sec - start_sec
        scheduler_times.append(schedule)

    mean_bench = {name: [] for name in benchmarks}
    std_bench = {name: [] for name in benchmarks}
    for name in benchmarks:
        mean_bench[name] = statistics.mean(times[name])
        std_bench[name] = statistics.stdev(times[name])
    
    mean_scheduler = statistics.mean(scheduler_times)  
    std_scheduler = statistics.stdev(scheduler_times)

    print('Scheduler meantime')
    print(mean_scheduler)
    print('Scheduler std')
    print(std_scheduler)
    print("benchmarks mean")
    print(mean_bench)
    print("benchmarks std")
    print(std_bench)


  
if __name__ == "__main__":
    calculate()
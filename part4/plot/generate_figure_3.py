import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pytz
from datetime import datetime
from dateutil import parser
import json
import matplotlib.patches as mpatches

sns.set_theme()

benchmarks = ['dedup', 'vips', 'radix','freqmine', 'canneal', 'ferret', 'blackscholes' ]
benchmarks_labels = ['dedup node-c', 'vips node-c', 'radix node-c','freqmine node-c', 'canneal node-b', 'ferret node-b', 'blackscholes node-a']
colors = ['#CCACCA', '#CC0A00', '#00CCA0', '#0CCA00', '#CCCCAA', '#AACCCA', '#CCA000']

def get_benchmark_times(data, benchmark, offset):
    start_times = []
    end_times = []
    for point in (data):
        if benchmark in point['metadata']['name']:
            start = point['status']['containerStatuses'][0]['state']['terminated']['startedAt']
            end = point['status']['containerStatuses'][0]['state']['terminated']['finishedAt']
            start_sec= transform_date_string(start)
            end_sec = transform_date_string(end)
            start_sec -=offset
            end_sec -=offset
            start_times.append(start_sec)
            end_times.append(end_sec)
    return start_times , end_times
        
def get_memcached_start(unix_timestamps, init):
    start_times = []
    for unix_timestamp in unix_timestamps:
        unix_timestamp /=1000
        ts = int(unix_timestamp)
        start = datetime.fromtimestamp(ts, tz= pytz.UTC)
        start_time = start.hour*3600 + start.minute * 60 + start.second - init
        start_times.append(start_time)
    return start_times

def transform_date_string(str):
    time = datetime.strptime(str,"%Y-%m-%dT%H:%M:%SZ")
    sec= time.hour*3600 + time.minute*60 + time.second
    return sec

def create_figures():

    for i in range(3):
        mem_file_path = f'part3/plot/memcached_results_run_{i}.txt'
        res_file_path = f'part3/plot/results_run_{i}.json'
        result_mem = pd.read_csv(mem_file_path, delim_whitespace=True)
        res_file = open(res_file_path)
        results = json.load(res_file)
        result_mem["p95"] = result_mem["p95"].divide(1000.0)  # convert to ms
        #TODO add column for cpu
        result_items = results['items']
        max = 0
        end_times_str = []
        for element in result_items:
            el = element['status']['containerStatuses'][0]['state']
            if 'terminated' not in el:
                continue
            end_times_str.append(el['terminated']['finishedAt'])

        for str in end_times_str:
            second = transform_date_string(str)
            if (second) > max:
                max = second

        min = 50000000
        start_times_str = []
        for element in result_items:
            el = element['status']['containerStatuses'][0]['state']
            if 'terminated' not in el:
                continue
            start_times_str.append(el['terminated']['startedAt'])

        for str in start_times_str:
            second = transform_date_string(str)
            if (second) < min:
                min = second

        start_sec= min 
        end_sec = max  
        runtimes_start = {name: [] for name in benchmarks}
        runtimes_end = {name: [] for name in benchmarks}

        for name in benchmarks:
            runtimes_start[name], runtimes_end[name] = get_benchmark_times(result_items, name, start_sec)

        fig = plt.figure(figsize=(8, 5))
        length = int(end_sec - start_sec)
        plt_95p, plt_jobs, plt_cpu = fig.subplots(3, 1, gridspec_kw={'height_ratios': [6, 3, 6]})

        plt_jobs.set_yticks(range(7))
        plt_jobs.set_yticklabels(benchmarks_labels)
        plt_jobs.set_ylim([-1, 7])
        plt_jobs.set_xlabel("Time [s]")
        plt_jobs.set_xlim([0, length])
        plt_jobs.set_xticks(range(0, length + 1, 50))
        plt_jobs.grid(True)
        for j, name in enumerate(benchmarks):
            color = colors[j]
            for k in enumerate(runtimes_start[name]):
                plt_jobs.hlines(y=j, xmin=runtimes_start[name][k], xmax=runtimes_end[name][k], color=color, linewidth=3)
                plt_jobs.plot(runtimes_start[name][k],j,'.', color=color) 
                plt_jobs.plot(runtimes_end[name][k],j,'x', color=color)

        plt_95p.set_xlim([0, length])
        plt_95p.set_xlabel("Time [s]")
        plt_95p.set_xticks(range(0, length, 50))
        plt_95p.grid(True)

        plt_95p.set_ylabel("95th Percentile Latency [ms]")
        plt_95p.tick_params(axis='y', labelcolor='tab:blue')
        plt_95p.set_ylim([0, 1.0])
        plt_95p.set_yticks(np.arange(0, 1.0, 0.1))
        start = get_memcached_start(result_mem["ts_start"],start_sec)
        plt_95p_left = plt_95p.plot(start, result_mem["p95"], alpha=0.8, label='p95', color = 'tab:purple')

        plt_95p_right = plt_95p_left.twinx()
        plt_95p_right.set_ylabel("Achieved QPS")
        plt_95p_right.set_ylim([0,130000])
        plt_95p_right.set_yticks(range(0, 100001, 10000),
                          labels=(f'{i}k' for i in range(0, 101, 10)))
        plt_95p_right.set_yticks(range(0, 100000, 10000), minor=True)
        plt_95p_right.tick_params(axis='y', labelcolor='tab:green')

        plt_95p_right.plot(start, result_mem["QPS"], alpha=0.8, label='qps', color = 'tab:cyan')

        plt_cpu.set_xlim([0, length])
        plt_cpu.set_xlabel("Time [s]")
        plt_cpu.set_xticks(range(0, length, 50))
        plt_cpu.grid(True)


        plt_cpu.set_ylabel("CPU Utilization [%]")
        plt_cpu.tick_params(axis='y', labelcolor='tab:blue')
        plt_cpu.set_ylim([0, 1.0])
        plt_cpu.set_yticks(np.arange(0, 1.0, 0.1))
        plt_cpu_left = plt_cpu.plot(start, result_mem["cpu"], alpha=0.8, label='cpu', color = 'tab:red')

        plt_cpu_right = plt_cpu_left.twinx()
        plt_cpu_right.set_ylabel("Achieved QPS")
        plt_cpu_right.set_ylim([0,130000])
        plt_cpu_right.set_yticks(range(0, 100001, 10000),
                          labels=(f'{i}k' for i in range(0, 101, 10)))
        plt_cpu_right.set_yticks(range(0, 100000, 10000), minor=True)
        plt_cpu_right.tick_params(axis='y', labelcolor='tab:green')


        plt_cpu_right.plot(start, result_mem["QPS"], alpha=0.8, label='qps', color = 'tab:cyan')

        plt.subplots_adjust(hspace=0.2, bottom=0.2)

        fig.tight_layout()
        #plt.show()
        fig.savefig(f'part4/plot/figure_4_3_run{i}.png')

  
if __name__ == "__main__":
    create_figures()
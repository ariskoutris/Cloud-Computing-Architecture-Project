import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import itertools
from datetime import datetime
from dateutil import parser
import json
import matplotlib.patches as mpatches

sns.set_theme()

benchmarks = ['blackscholes', 'freqmine', 'vips', 'dedup', 'radix', 'canneal', 'ferret']
benchmarks_labels = ['blackscholes-client a', 'freqmine-client c', 'vips-client b', 'dedup-client c', 'radix-client b', 'canneal-client c', 'ferret-client b']
colors = ['#CCA000', '#0CCA00', '#CC0A00', '#CCACCA', '#00CCA0', '#CCCCAA', '#AACCCA']
runtimes_start = {name: [] for name in benchmarks}
runtimes_end = {name: [] for name in benchmarks}

def get_benchmark_times(data, benchmark):
    for point in (data):
        if benchmark in point['metadata']['name']:
            start = point['status']['containerStatuses'][0]['state']['terminated']['startedAt']
            end = point['status']['containerStatuses'][0]['state']['terminated']['finishedAt']
            start_sec= transform_date_string(start)
            end_sec = transform_date_string(end)
            return start_sec , end_sec
        
def get_memcached_start(unix_timestamps, init):
    start_times = []
    for unix_timestamp in unix_timestamps:
        unix_timestamp /=1000
        ts = int(unix_timestamp)
        start = datetime.fromtimestamp(ts)
        start_time = start.minute * 60 + start.second - init
        start_times.append(start_time)
    return start_times

def get_memcached_width(unix_timestamp_starts, unix_timestamp_ends):
    widths = []

    for unix_timestamp_start, unix_timestamp_end in zip(unix_timestamp_starts, unix_timestamp_ends):
        unix_timestamp_start /=1000
        ts = int(unix_timestamp_start)
        start = datetime.fromtimestamp(ts)
        start_time = start.minute * 60 + start.second

        unix_timestamp_end /=1000
        ts2 = int(unix_timestamp_end)
        end = datetime.fromtimestamp(ts2)
        end_time = end.minute * 60 + end.second

        width = end_time - start_time
        if (width < 0):
            width = 0
        widths.append(width)
    return widths

def transform_date_string(str):
    time = datetime.strptime(str,"%Y-%m-%dT%H:%M:%SZ")
    sec= time.minute*60 + time.second
    return sec

def create_figures():

    for i in range(3):
        mem_file_path = f'part3/plot/memcached_results_run_{i}.txt'
        res_file_path = f'part3/plot/results_run_{i}.json'
        result_mem = pd.read_csv(mem_file_path, delim_whitespace=True)
        res_file = open(res_file_path)
        results = json.load(res_file)
        result_mem["p95"] = result_mem["p95"].divide(1000.0)  # convert to ms
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

        for name in benchmarks:
            s, e = get_benchmark_times(result_items, name)
            runtimes_start[name].append(s - start_sec)
            runtimes_end[name].append(e - start_sec)

        fig = plt.figure(figsize=(8, 5))
        length = int(end_sec - start_sec)
        plt_95p, plt_jobs = fig.subplots(2, 1, gridspec_kw={'height_ratios': [6, 3]})

        plt_jobs.set_yticks(range(7))
        plt_jobs.set_yticklabels(benchmarks_labels)
        plt_jobs.set_ylim([-1, 7])
        plt_jobs.set_xlim([0, length])
        plt_jobs.set_xticks(range(0, length + 1, 50))
        plt_jobs.grid(True)
        for j, name in enumerate(benchmarks):
            color = colors[j]

            plt_jobs.hlines(y=j, xmin=runtimes_start[name][i], xmax=runtimes_end[name][i], color=color, linewidth=3)
            plt_jobs.plot(runtimes_start[name][i],j,'.', color=color) 
            plt_jobs.plot(runtimes_end[name][i],j,'x', color=color)

        plt_95p.set_xlim([0, length])
        plt_95p.set_xlabel("Time [s]")
        plt_95p.set_xticks(range(0, length, 50))
        plt_95p.grid(True)
        plt_95p.set_ylabel("95th Percentile Latency [ms]")
        plt_95p.tick_params(axis='y', labelcolor='tab:blue')
        plt_95p.set_ylim([0, 1.0])
        plt_95p.set_yticks(np.arange(0, 1.0, 0.1))
        start = get_memcached_start(result_mem["ts_start"],start_sec)
        width = get_memcached_width(result_mem["ts_start"],result_mem["ts_end"])
        plt_95p.bar(start, result_mem["p95"], align='center', width=width)

        plt.subplots_adjust(hspace=0.2, bottom=0.2)
        fig.tight_layout()
        #plt.show()
        fig.savefig(f'part3/figure_3_run{i}.png')


def create_unified_figure():

    for i in range(3):
        mem_file_path = f'part3/plot/memcached_results_run_{i}.txt'
        res_file_path = f'part3/plot/results_run_{i}.json'
        result_mem = pd.read_csv(mem_file_path, delim_whitespace=True)
        res_file = open(res_file_path)
        results = json.load(res_file)
        result_mem["p95"] = result_mem["p95"].divide(1000.0)  # convert to ms
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

        for name in benchmarks:
            s, e = get_benchmark_times(result_items, name)
            runtimes_start[name].append(s - start_sec)
            runtimes_end[name].append(e - start_sec)

        fig = plt.figure(figsize=(8, 5))
        length = int(end_sec - start_sec)


        plt.xlim([0, length])
        plt.xlabel("Time [s]")
        plt.xticks(range(0, length, 50))
        plt.grid(True)
        plt.ylabel("95th Percentile Latency [ms]")
        plt.tick_params(axis='y', labelcolor='tab:blue')
        plt.ylim([0, 1.0])
        plt.yticks(np.arange(0, 1.0, 0.1))
        start = get_memcached_start(result_mem["ts_start"],start_sec)
        width = get_memcached_width(result_mem["ts_start"],result_mem["ts_end"])
        plt.bar(start, result_mem["p95"], align='center', width=width)


        plt.hlines(y=0.1, xmin=runtimes_start['blackscholes'][i], xmax=runtimes_end['blackscholes'][i], color=colors[0], linewidth=3)
        plt.plot(runtimes_start['blackscholes'][i],0.1,'.', color=colors[0]) 
        plt.plot(runtimes_end['blackscholes'][i],0.1,'x', color=colors[0])
        
        plt.hlines(y=0.2, xmin=runtimes_start['freqmine'][i], xmax=runtimes_end['freqmine'][i], color=colors[1], linewidth=3)
        plt.plot(runtimes_start['freqmine'][i],0.2,'.', color=colors[1]) 
        plt.plot(runtimes_end['freqmine'][i],0.2,'x', color=colors[1])
        plt.hlines(y=0.2, xmin=runtimes_start['canneal'][i], xmax=runtimes_end['canneal'][i], color=colors[5], linewidth=3)
        plt.plot(runtimes_start['canneal'][i],0.2,'.', color=colors[5]) 
        plt.plot(runtimes_end['canneal'][i],0.2,'x', color=colors[5])
        plt.hlines(y=0.2, xmin=runtimes_start['dedup'][i], xmax=runtimes_end['dedup'][i], color=colors[3], linewidth=3)
        plt.plot(runtimes_start['dedup'][i],0.2,'.', color=colors[3]) 
        plt.plot(runtimes_end['dedup'][i],0.2,'x', color=colors[3])

        plt.hlines(y=0.3, xmin=runtimes_start['vips'][i], xmax=runtimes_end['vips'][i], color=colors[2], linewidth=3)
        plt.plot(runtimes_start['vips'][i],0.3,'.', color=colors[2]) 
        plt.plot(runtimes_end['vips'][i],0.3,'x', color=colors[2])
        plt.hlines(y=0.3, xmin=runtimes_start['ferret'][i], xmax=runtimes_end['ferret'][i], color=colors[6], linewidth=3)
        plt.plot(runtimes_start['ferret'][i],0.3,'.', color=colors[6]) 
        plt.plot(runtimes_end['ferret'][i],0.3,'x', color=colors[6])

        plt.hlines(y=0.4, xmin=runtimes_start['radix'][i], xmax=runtimes_end['radix'][i], color=colors[4], linewidth=3)
        plt.plot(runtimes_start['radix'][i],0.4,'.', color=colors[4]) 
        plt.plot(runtimes_end['radix'][i],0.4,'x', color=colors[4])

        legends_handles = []
        for k, name in enumerate(benchmarks_labels):
            patch = mpatches.Patch(color=colors[k], label=name)
            legends_handles.append(patch)
        plt.legend(handles=legends_handles)

        fig.tight_layout()
        #plt.show()
        fig.savefig(f'part3/figure_3_unified_run{i}.png')





    
    
if __name__ == "__main__":
    create_figures()
    create_unified_figure()

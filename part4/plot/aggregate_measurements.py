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

def get_memcached_start(unix_timestamps, init):
    start_times = []
    for unix_timestamp in unix_timestamps:
        unix_timestamp /=1000
        ts = int(unix_timestamp)
        start = datetime.fromtimestamp(ts, tz= pytz.UTC)
        start_time = start.hour*3600 + start.minute * 60 + start.second - init
        start_times.append(start_time)
    return start_times

def aggregate():

    mem_file_path = f'part3/plot/memcached_results_run.txt'
    cpu_file_path = f'part3/plot/results_run_.txt'
    result_mem = pd.read_csv(mem_file_path, delim_whitespace=True)
    cpu_file = pd.read_csv(cpu_file_path, delim_whitespace=True)
    cpu_util = []
    for index, row in result_mem.iterrows():
        start = row['ts_start']
        end = row['ts_start']
        cpu = 0
        count = 0
        for index2, row2 in cpu_file.iterrows():
            if (row2['timestamp'] > start & row2['timestamp'] <= end):
                cpu += row2['cpu']
                count += 1
        final_val = cpu / count
        cpu_util.append(final_val)
    result_mem.assign(cpu_utilization=cpu_util)
    result_mem.to_csv(mem_file_path, sep='\t')
        

        

  
if __name__ == "__main__":
    create_figures()
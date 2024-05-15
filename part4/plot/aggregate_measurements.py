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

    mem_file_path = f'part4/results/memcached_results_T2_C2.txt'
    cpu_file_path = f'part4/results/cpu_util_T2_C2.csv'
    result_mem = pd.read_csv(mem_file_path, delim_whitespace=True)
    cpu_file = pd.read_csv(cpu_file_path)
    result_mem['ts_start']= result_mem['ts_start']/1000
    result_mem['ts_end']= result_mem['ts_end']/1000

    cpu_util = []
    for index, row in result_mem.iterrows():
        start = row['ts_start']
        end = row['ts_end']
        cpu = 0
        count = 0
        for index2, row2 in cpu_file.iterrows():
            if (row2['timestamp'] >= start and row2['timestamp'] <= end):
                cpu += row2['cpu']
                count += 1
        final_val = cpu / count
        cpu_util.append(final_val)
    result_mem.insert(20, "cpu", cpu_util, True)
    result_mem.to_csv(mem_file_path, sep='\t')
        

        

  
if __name__ == "__main__":
    aggregate()
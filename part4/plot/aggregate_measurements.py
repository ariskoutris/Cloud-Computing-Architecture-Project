import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pytz
from datetime import datetime
from dateutil import parser
import json
import matplotlib.patches as mpatches

utc=pytz.UTC
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

def aggregate_times():

    mem_file_path = f'part4/results/4_4/mcperf.txt'
    result_mem = pd.read_csv(mem_file_path, delim_whitespace=True)
    start = 1715958568066
    end = 1715959468641
    intervals = 180
    counter = ((end - start)/intervals)
    ts_start = []
    ts_end = []
    prev = start
    for index, row in result_mem.iterrows():
        ts_start.append(prev)
        ending = prev + counter
        ts_end.append(ending)
        prev = ending

    result_mem.insert(18, "ts_start", ts_start, True)
    result_mem.insert(19, "ts_end", ts_end, True)
    mem_file_path = f'part4/plot/results_4_3/memcached_3.txt'
    result_mem.to_csv(mem_file_path, sep='\t')

def transform_unix_time(unix_timestamp):
    unix_timestamp /=1000
    ts = int(unix_timestamp)
    start = datetime.fromtimestamp(ts, tz= pytz.UTC)
    return start

def aggregate_cores():
    mem_file_path = f'part4/plot/results_4_3/memcached_3.txt'
    cpu_file_path = f'part4/plot/results_4_3/jobs_3.txt'

    result_mem = pd.read_csv(mem_file_path, delim_whitespace=True)
    cpu_file = pd.read_csv(cpu_file_path, delim_whitespace=True)

    cpu_cores = []
    count = 1
    for index, row in result_mem.iterrows():
        start = transform_unix_time(row['ts_start'])
        end = transform_unix_time(row['ts_end'])

        for index2, row2 in cpu_file.iterrows():
            if (row2['job']=='memcached'):
                ttime = datetime.strptime(row2['timestamp'],"%Y-%m-%dT%H:%M:%S.%f") 
                time = ttime.replace(tzinfo=utc)
                if (time >= start and time <= end):
                    commas = row2['cores'].find(',')
                    if commas != -1 :
                        count = 2
                    else:
                        count = 1

        cpu_cores.append(count)

    result_mem.insert(1, "cpu_cores", cpu_cores, True)
    result_mem.to_csv(mem_file_path, sep='\t')

  
if __name__ == "__main__":
    aggregate_times()
    aggregate_cores()
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

sns.set_theme()

configurations = ['1 core', '2 cores']
label_map = {key: key for key in configurations}
file_map = ['T2_C1','T2_C2']


def create_figure(meas, id):
    fig = plt.figure(figsize=(8, 6))

    #dual y axes
    fig_95 = fig.gca()
    fig_cpu = fig_95.twinx()

    fig_95.set_xlabel('achieved QPS', fontsize=15)
    plt.xlim([0,130000])
    plt.xticks(range(0, 130001, 10000),
                          labels=(f'{i}k' for i in range(0, 131, 10)))
    
    fig_95.set_ylabel('$95^{th}$ Percentile Latency (ms)', fontsize=15)
    fig_cpu.set_ylabel('CPU Utilization (%)', fontsize=15)
    
    if id==0:
        fig_95.set_ylim([0, 2.2])
        fig_95.set_yticks(np.arange(0, 2.4, 0.2))

        fig_cpu.set_ylim([0, 100])
        fig_cpu.set_yticks(range(0, 110, 10))
    else:
        fig_95.set_ylim([0, 2.0])
        fig_95.set_yticks(np.arange(0, 2.2, 0.2))

        fig_cpu.set_ylim([0, 200])
        fig_cpu.set_yticks(range(0, 210, 10))

    meas['p95'] /= 1000
    fig_95.plot(meas['QPS'], meas['p95'], alpha=0.8, label='p95', color = 'tab:purple', marker = '.')
    fig_95.axhline(y=1.0, color='tab:gray', linewidth=3, linestyle='dotted', label='SLO')

    fig_cpu.plot(meas['QPS'], meas['cpu'], alpha=0.8, label='cpu', color = 'royalblue', marker = '.')

    lines, labels = fig_95.get_legend_handles_labels()
    lines2, labels2 = fig_cpu.get_legend_handles_labels()
    fig_cpu.legend(lines + lines2, labels + labels2, loc=0)    
    
    plt.tight_layout()
    
    return fig
    
if __name__ == "__main__":
    for id, configuration in enumerate(file_map):
        file_path = f'part4/plot/results_4_1d/memcached_results_{configuration}.txt'
        conf = configurations[id]
        measurements = pd.read_csv(file_path, delim_whitespace=True)
        fig = create_figure(measurements, id)
        fig.savefig(f'part4/plot/figure_4_1d_{configuration}.png', dpi=300)
        
    
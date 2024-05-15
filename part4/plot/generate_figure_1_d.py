import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

sns.set_theme()

configurations = ['1 core', '2 cores']
label_map = {key: key for key in configurations}
file_map = ['T=1,C=1','T=1,C=2']


def create_figure(meas, configuration):
    fig = plt.figure(figsize=(8, 6))

    #dual y axes
    fig_95 = fig.gca()
    fig_cpu = fig_95.twinx()

    fig_95.set_xlabel('achieved QPS', fontsize=15)
    fig_95.set_xlim([0,130000])
    fig_95.set_xticks(range(0, 130001, 10000),
                          labels=(f'{i}k' for i in range(0, 131, 10)))
    fig_95.set_xticks(range(0, 130000, 10000), minor=True)
    
    fig_95.set_ylim([0, 2.0])
    fig_95.set_ylabel('$95^{th}$ Percentile Latency (ms)', fontsize=15)
    fig_95.set_yticks(np.arange(0, 1.0, 0.1))

    fig_cpu.set_ylabel('CPU Utilization (%)', fontsize=15)
    fig_cpu.set_ylim([0, 100])
    fig_cpu.set_yticks(range(0, 100, 25))

    fig.title(f'memcached Performance {configuration}', fontsize=16)


    meas['95'] /= 1000
    fig_95.plot(meas['QPS'], meas['p95'], alpha=0.8, label='p95', color = 'tab:purple')
    fig_95.hlines(y=1.0, color='tab:gray', linewidth=3, linestyles='dotted', label='SLO')

    fig_cpu.plot(meas['QPS'], cpu, alpha=0.8, label='cpu', color = 'royalblue')#TODO CPU UTILIZATION

    fig.legend(loc='upper right', fontsize=12)
    
    
    plt.tight_layout()
    
    return fig
    
if __name__ == "__main__":
    for id, configuration in enumerate(file_map):
        file_path = f'results/memached_results_{configuration}.csv'
        conf = configurations[id]
        measurements = pd.read_csv(file_path)
        fig = create_figure(measurements, configuration)
        fig.savefig(f'figure_4_1d_{configuration}.png', dpi=300)
        
    
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

sns.set_theme()

configurations = ['1 thread - 1 core', '1 thread - 2 cores', '2 threads - 1 core', '2 threads - 2 cores']
label_map = {key: key for key in configurations}
file_map = ['T=1,C=1','T=1,C=2','T=2,C=1','T=2,C=2']

def aggregate_metrics(df):
    means = df.groupby('target').agg({'QPS': 'mean', 'p95': 'mean'}).sort_values('QPS')
    errs = df.groupby('target').agg({'QPS': 'std', 'p95': 'std'}).loc[means.index]
    return means, errs

def create_figure(df_list, xlim=(0,125000), ylim=(0,2.2), use_error_bars=True):
    fig = plt.figure(figsize=(8, 6))
    marker_styles = ['o', 's', 'D', '^', '<', '>', '*']
    line_styles = ['-', '--', '-.', ':']
    for idx, configuration in enumerate(configurations):
        means, errs = aggregate_metrics(df_list[configuration])
        marker = marker_styles[idx % len(marker_styles)]
        line_style = line_styles[idx % len(line_styles)]
        if use_error_bars:
            plt.errorbar(means['QPS'], means['p95']/1000, xerr=errs['QPS'], yerr=errs['p95']/1000,
                         fmt=line_style+marker, markersize=5, linewidth=2, elinewidth=0.8, capsize=1.5,
                         alpha=0.8, label=label_map[configuration])
        else:
            plt.plot(means['QPS'], means['p95']/1000, line_style+marker, markersize=5, linewidth=2,
                     alpha=0.8, label=label_map[configuration])
    
    plt.xlabel('Achieved QPS', fontsize=15)
    plt.ylabel('$95^{th}$ Percentile Latency (ms)', fontsize=15)
    plt.title('memcached performance (3 run average)', fontsize=16)
    plt.legend(fontsize=13)
    plt.xticks(range(0, 125001, 15000),
                          labels=(f'{i}k' for i in range(0, 125, 15)))
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)
    plt.yticks(np.arange(0, 2.4, 0.2))
    
    plt.xlim(*xlim)
    plt.ylim(*ylim)
    plt.tight_layout()
    
    return fig
    
if __name__ == "__main__":
    result_dfs = {}
    for id, configuration in enumerate(file_map):
        file_path = f'part4/plot/results_4_1a/memcached_results_{configuration}.txt'
        conf = configurations[id]
        result_dfs[conf] = pd.read_csv(file_path)
        
    fig = create_figure(result_dfs)
    fig.savefig(f'part4/plot/figure_4_1a.png', dpi=300)
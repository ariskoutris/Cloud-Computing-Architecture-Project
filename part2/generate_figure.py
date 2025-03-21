import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import itertools

sns.set_theme()

benchmarks = ['blackscholes', 'freqmine', 'vips', 'dedup', 'radix', 'canneal', 'ferret']
label_map = {key: key for key in benchmarks }
marker = itertools.cycle(('.', 's', 'X', '^', '*', 'p', '>')) 

def create_figure(df_list):
    fig = plt.figure(figsize=(8, 6))

    # linear 
    plt.errorbar(
        x=range(1, 17),
        y=range(1, 17),
        label='linear speedup',
        linestyle='--',
        markersize=8,
        markerfacecolor="grey",
        color='grey',
        capsize=4
    )
    # sub-linear
    plt.errorbar(
        x=range(1, 17),
        y=[(i/(1+0.005*(i-1))) for i in range(1, 17)],
        label='sub-linear speedup',
        linestyle=':',
        markersize=8,
        markerfacecolor="grey",
        color='black',
        capsize=4
    )
    # super-linear
    plt.errorbar(
        x=range(1, 17),
        y=[(i/(1-0.03*((i-1) +0.0005*i*(i-1)))) for i in range(1, 17)],
        label='super-linear speedup',
        linestyle='-.',
        markersize=8,
        markerfacecolor="grey",
        color='black',
        capsize=4
    )
    for benchmark in benchmarks:
        plt.plot(df_list['Thread'], df_list[benchmark], marker=next(marker), markersize='4', linewidth=1, label=label_map[benchmark])   
    plt.xlabel('Number of threads')
    plt.ylabel('Speedupx')
    plt.xlim(0,9)
    plt.ylim(1, 6.5)
    plt.title('Speedup vs Parallel Workload (Normalized time)')
    plt.legend()
    plt.tight_layout()
    return fig
    
if __name__ == "__main__":
    file_path = f'results_B/results_B_flipped_cols.csv'
    result_dfs = pd.read_csv(file_path)
    fig = create_figure(result_dfs)
    fig.savefig('plots/figure_2b.png')
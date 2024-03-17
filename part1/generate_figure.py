import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme()

interefence_types = ['no_interference', 'ibench-cpu', 'ibench-l1d', 'ibench-l1i', 'ibench-l2', 'ibench-llc', 'ibench-membw']

def parse_file_to_dataframe(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().strip().split('\n')

    sections = [[]]
    for line in lines:
        if line.strip():  
            sections[-1].append(line)
        else:
            sections.append([])

    dfs = []
    for section_index, section in enumerate(sections):
        if section and not section[0].startswith(("Warning", "CPU Usage")):
            headers = section[0].split()
            data = [line.split() for line in section[1:] if not line.startswith(("Warning", "CPU Usage"))]
            df_section = pd.DataFrame(data, columns=headers)
            for column in headers[1:]:
                df_section[column] = pd.to_numeric(df_section[column], errors='coerce')
            df_section['run_index'] = section_index + 1
            dfs.append(df_section)

    return pd.concat(dfs, ignore_index=True)

def aggregate_metrics(df):
    means = df.groupby('target').agg({'QPS': 'mean', 'p95': 'mean'}).sort_values('QPS')
    errs = df.groupby('target').agg({'QPS': 'std', 'p95': 'std'}).loc[means.index]
    return means, errs

def create_figure(df_list):
    fig = plt.figure(figsize=(8, 6))
    for interference_type in interefence_types:
        means, errs = aggregate_metrics(df_list[interference_type])
        plt.errorbar(means['QPS'], means['p95']/1000, xerr=errs['QPS'],  yerr=errs['p95']/1000, fmt='--o', markersize='4', elinewidth=1, capsize=3, label=interference_type)   
    plt.xlabel('QPS')
    plt.ylabel('$95^{th}$ Percentile Latency (ms)')
    plt.xlim(0,55000)
    plt.ylim(0, 10)
    plt.title('QPS vs Latency (3 Run Average)')
    plt.legend()
    plt.tight_layout()
    return fig
    
if __name__ == "__main__":
    result_dfs = {}
    for interference_type in interefence_types:
        file_path = f'{interference_type}.txt'
        result_dfs[interference_type] = parse_file_to_dataframe(file_path)
    fig = create_figure(result_dfs)
    fig.savefig('figure.png')
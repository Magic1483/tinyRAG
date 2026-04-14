from typing import Literal
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

"""
Generate report from collected data
1. produce summary report (by mode)
2. produce per question metrics (kw_score,mrr,hit@5,avg_answer_length)
3. generate plot per each metric (seaborn)
"""

IMAGS_PATH="../../docs/imgs"

def draw_line_plot(data,x,y,hue,title,legend_title,save_as,
                plot_type:Literal['line','bar','strip']='line'):
    """
    Draw lineplot , x/y_title is Capitilized metric
    """
    plt.figure(figsize=(10,5.5))
    plt.title(title)
    match plot_type:
        case 'bar':
            sns.barplot(data=df, x=x, y=y, hue=hue)
        case 'strip':
            sns.stripplot(data=df, x=x, y=y, hue=hue, dodge=True, jitter=0.08)
        case 'line':
            sns.lineplot(
            data=data,
            x=x,
            y=y,
            marker="o",
            hue=hue,
            linewidth=1.8,
            alpha=0.8,
        )

    plt.xticks(rotation=0)
    plt.xlabel(str(x).capitalize())
    plt.ylabel(str(y).capitalize())
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.18)
    if legend_title:
        plt.legend(title=legend_title, loc="lower left",framealpha=0.65)
    if save_as:
        plt.savefig(f"{IMAGS_PATH}/{save_as}.png", dpi=300,bbox_inches='tight')
    plt.close()



df = pd.read_csv("results/metrics.csv")
mode_order = ["vector", "vector+bm25", "vector+hyde", "vector+bm25+hyde"]
df['mode'] = pd.Categorical(df['mode'],categories=mode_order,ordered=True)
df.sort_values("mode")

# add question_id
question_order = df['question'].drop_duplicates().to_list()
qid_map = {q:i+1 for i,q in enumerate(question_order)}
df['question_id'] = df['question'].map(qid_map)

# Summary by "mode"
summary = (
    df.groupby("mode", as_index=False)
        .agg(
          avg_kw_score=("kw_score", "mean"),
          avg_hit_at_5=("hit_at_5", "mean"),
          avg_mrr=("mrr", "mean"),
          avg_answer_len=("answer_len", "mean"),
    ))
summary['abs_answer_len'] = summary['avg_answer_len']
summary["avg_answer_len"] = (
    summary["avg_answer_len"] / summary["avg_answer_len"].mean())

summary['mode'] = pd.Categorical(summary['mode'],categories=mode_order,ordered=True)
summary.sort_values("mode")

summary.to_csv("results/metrics_summary_by_mode.csv", index=False)
print(summary)

# Separate metrics kw_score/hit@5/Mrr
kw = df.pivot(index="question", columns="mode", values="kw_score").reset_index()
hit = df.pivot(index="question", columns="mode", values="hit_at_5").reset_index()
mrr = df.pivot(index="question", columns="mode", values="mrr").reset_index()

kw.to_csv("results/pivot_kw_score.csv", index=False)
hit.to_csv("results/pivot_hit_at_5.csv", index=False)
mrr.to_csv("results/pivot_mrr.csv", index=False)



# draw summary plot
sns.set_theme(style='darkgrid',context='talk')
metrics = ["avg_kw_score", "avg_hit_at_5", "avg_mrr"]
long_df = summary.melt(
    id_vars="mode",
    value_vars=[m for m in metrics if m in summary.columns],
    var_name="metric",
    value_name="value"
)
draw_line_plot(long_df,'mode','value','metric','Summary by mode',"Metric",'summary_by_mode')
print(f'[*] save summary plot')

# draw per metric plots
metrics = ["kw_score", "mrr",'hit_at_5']
for metric in [m for m in metrics if m in df.columns]:
    print(f'[*] save {metric}')
    plot_type = 'strip' if metric == 'hit_at_5' else 'line'
    draw_line_plot(df,'question_id',metric,'mode',
                  f"Pivot by {metric}","Mode",f'pivot_{metric}',plot_type)
    

import pandas as pd

df = pd.read_csv("results/metrics.csv")

summary = (
    df.groupby("mode", as_index=False)
        .agg(
          avg_kw_score=("kw_score", "mean"),
          avg_hit_at_5=("hit_at_5", "mean"),
          avg_mrr=("mrr", "mean"),
          avg_answer_len=("answer_len", "mean"),
    )
)
summary["avg_answer_len"] = (
    summary["avg_answer_len"] / summary["avg_answer_len"].mean()
)


summary.to_csv("results/metrics_summary_by_mode.csv", index=False)
print(summary)

kw = df.pivot(index="question", columns="mode", values="kw_score").reset_index()
hit = df.pivot(index="question", columns="mode", values="hit_at_5").reset_index()
mrr = df.pivot(index="question", columns="mode", values="mrr").reset_index()

kw.to_csv("results/pivot_kw_score.csv", index=False)
hit.to_csv("results/pivot_hit_at_5.csv", index=False)
mrr.to_csv("results/pivot_mrr.csv", index=False)
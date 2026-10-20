from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

GROUPS = {"Age": "age_group", "Length of stay": "stay_group", "Prior inpatient visits": "prior_inpatient_group", "Medication change": "medication_change", "Primary diagnosis group": "primary_diagnosis_group", "Admission type": "admission_type_id", "Race": "race"}

def grouped_rates(df: pd.DataFrame, col: str) -> pd.DataFrame:
    return df.groupby(col, dropna=False).readmit_30d.agg(encounters="size", early_readmissions="sum", early_readmit_rate="mean").reset_index()

def run_eda(df: pd.DataFrame, reports: Path) -> dict:
    figdir = reports / "figures"; figdir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    results = {"encounters": len(df), "unique_patients": int(df.patient_nbr.nunique()), "early_readmissions": int(df.readmit_30d.sum()), "early_readmit_rate": float(df.readmit_30d.mean())}
    for title, col in GROUPS.items():
        table = grouped_rates(df, col)
        table.to_csv(reports / f"readmission_by_{col}.csv", index=False)
        plot = table.sort_values("early_readmit_rate", ascending=False).head(20)
        fig, ax = plt.subplots(figsize=(10,5)); sns.barplot(data=plot, x=col, y="early_readmit_rate", ax=ax, color="#2878B5")
        ax.set(title=f"30-day readmission by {title.lower()} (n={len(df):,})", xlabel=title, ylabel="Encounter readmission rate")
        ax.tick_params(axis="x", rotation=35); fig.tight_layout(); fig.savefig(figdir / f"{col}.png", dpi=150); plt.close(fig)
    # Sensitivity cohort excludes death/hospice dispositions; primary estimates keep these rows.
    eligible = df[df.death_hospice_disposition == 0]
    results["death_hospice_rows"] = int(len(df)-len(eligible)); results["eligible_encounters"] = len(eligible); results["eligible_early_readmit_rate"] = float(eligible.readmit_30d.mean()) if len(eligible) else None
    (reports / "eda_summary.json").write_text(__import__('json').dumps(results, indent=2), encoding="utf-8")
    df.groupby(["readmitted"], dropna=False).size().rename("encounters").to_csv(reports / "outcome_distribution.csv")
    return results

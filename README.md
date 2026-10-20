# Diabetes Patient Journey & Readmission Analytics

An undergraduate portfolio project using encounter records from the UCI Diabetes 130-US Hospitals dataset. It measures encounter-level readmission within 30 days, describes patterns across patient and encounter groups, evaluates patient-grouped prediction models, and prepares outputs for SQLite and Power BI. This is a retrospective educational analysis, not a clinically validated decision system.

## Source and scope

Source: [UCI Machine Learning Repository, Diabetes 130-US Hospitals for Years 1999–2008](https://archive.ics.uci.edu/dataset/296/diabetes%2B130-us+hospitals%2Bfor%2Byears%2B1999-2008), DOI 10.24432/C5230J (CC BY 4.0). The records span 130 US hospitals and 1999–2008. One row represents an encounter; the same patient can occur multiple times. `readmit_30d=1` for `<30`, and 0 for `>30` or `NO`. Other target labels are dropped and counted. `?` is interpreted as missing.

## Reproduce on Windows / PowerShell

```powershell
cd C:\path\to\trinity2
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.run_pipeline
python -m pytest -q
```

The pipeline downloads and extracts the UCI archive to `data/raw/` when the CSV is absent, cleans it, writes `data/processed/cleaned_encounters.csv` and a SQLite database, runs descriptive analyses and models, and creates dashboard-ready CSVs. Raw and generated large data files are git-ignored. To rerun with a fresh download, remove the local raw CSV and rerun the pipeline.

Open notebooks with `jupyter notebook` from the project root. Run `01_exploratory_analysis.ipynb` and `02_readmission_model.ipynb` after the pipeline creates the cleaned CSV.

## Project layout

`src/` contains reusable ingestion, preprocessing, EDA, modeling, and reporting modules. `sql/analysis_queries.sql` includes standalone summaries and a death/hospice sensitivity comparison. `tests/` contains unit and integration checks. `reports/` receives charts, metrics, and execution summaries. `dashboard/powerbi_data/` contains Power BI import tables.

## Analytical decisions

- Primary descriptive cohort retains all eligible target rows, including death/hospice disposition; the sensitivity analysis excludes disposition IDs 11, 13, 14, 19, 20, and 21. These are disposition codes commonly denoting expired or hospice. Verify code mapping for a particular source release before reuse.
- Target rows outside `<30`, `>30`, `NO` are excluded. Duplicate full rows are removed and counted. Missing predictors are imputed within the training pipeline (median numeric, most frequent categorical) with an indicator for numeric missingness. In descriptive exports, missing categories remain visible.
- Encounter and patient identifiers, target source label, and the engineered disposition sensitivity flag are excluded from predictors. Readmission source label is never used as a model feature. Other discharge disposition and clinical encounter variables are available as features at discharge; prediction is retrospective and does not establish prospective availability for every field.
- Train/test split is grouped by `patient_nbr`; groups are never shared. The holdout is not tuned against. Class weighting is used for logistic regression and random forest; the prevalence classifier is the simple baseline.
- The score threshold is 0.5. In practical screening, a threshold should be selected with stakeholder input and validated on independent contemporary data.

## Measured results from this run

The actual UCI download and full pipeline run completed. The source had **101,766 encounters**, **71,518 unique patients**, **0 exact duplicate rows**, **374,017 missing cells**, and **0 invalid target rows removed**. The cleaned cohort retained all 101,766 encounters. There were 11,357 early readmissions (**11.16%**). Excluding the 2,423 death/hospice-flagged encounters as a sensitivity check gave 11.39% among 99,343 encounters.

The strongest descriptive gradient was prior inpatient use: rate rose from **8.44%** for zero prior visits (n=67,630) to **25.66%** for three or more (n=7,049). The 1–2 day stay group was 9.14% (n=31,432), versus 13.08% for 6–8 days (n=17,789). Medication change was associated with 11.82% versus 10.59% for no change. These are unadjusted associations, not causal effects.

On a fixed patient-grouped holdout of 20,153 encounters from 14,304 patients (10.67% positive), logistic regression had ROC-AUC **0.635**, precision **0.155**, recall **0.543**, F1 **0.242**, PR-AUC **0.182**. Random forest had ROC-AUC **0.660**, precision **0.190**, recall **0.393**, F1 **0.256**, PR-AUC **0.195**. The prevalence baseline had ROC-AUC 0.500 and PR-AUC 0.107. This modest holdout performance is not clinical validation. Full results and interpretation are in [the executive report](reports/executive_report.md) and machine-readable output in `reports/execution_summary.json`.

## Power BI Desktop

See [dashboard/README.md](dashboard/README.md). Import the CSVs from `dashboard/powerbi_data/` using **Get Data → Text/CSV**. Create three report pages: executive KPIs and age pattern; encounter and medication comparisons with slicers; and model comparison plus a confusion matrix. A `.pbix` has not been generated by this Python project.

## Limitations and next steps

The dataset is historical, drawn from a subset of US hospitals, and has substantial missingness (including weight and payer/specialty fields). Encounters are repeated within patient, diagnoses and care patterns may reflect coding, and the readmission label is encounter based. The grouped split protects against patient overlap but is not a temporal or hospital-level validation. A risk score is not a clinical recommendation. Next steps include time-based and hospital-held-out validation, subgroup performance and calibration review, threshold analysis, and consultation with clinicians and operational stakeholders before any use.

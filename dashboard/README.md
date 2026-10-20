# Power BI dashboard guide

Import CSV files from `dashboard/powerbi_data/` with **Home → Get data → Text/CSV**. Load `executive_kpis.csv`, `by_age_group.csv`, `by_stay_group.csv`, `by_prior_inpatient_group.csv`, `by_medication_change.csv`, `by_admission_type_id.csv`, `by_primary_diagnosis_group.csv`, `encounters_powerbi.csv`, and `model_metrics.csv` (available after a successful full run). Confirm `early_readmit_rate` is decimal and format it as percentage. For slicers that filter encounter visuals, build those visuals from `encounters_powerbi.csv` and define measures:

```DAX
Encounters = COUNTROWS(encounters_powerbi)
Early Readmissions = SUM(encounters_powerbi[readmit_30d])
Early Readmit Rate = DIVIDE([Early Readmissions], [Encounters])
Unique Patients = DISTINCTCOUNT(encounters_powerbi[patient_nbr])
```

Use the rate fields as averages only when using the pre-aggregated category tables, and do not combine those aggregates with encounter-level slicers unless you add matching dimension tables and relationships.

## Page 1 — Executive Overview

Use the four fields in `executive_kpis.csv` as cards: total encounters, unique patients, early readmissions, early-readmission rate. Add a bar chart with `by_age_group.csv` age groups on axis and rate as value; show encounter count in tooltip.

## Page 2 — Patient and Encounter Analysis

Add rate-by-category bars for stay, prior inpatient visits, medication change, and primary diagnosis from the encounter table, using the measures above. Add slicers for age group, admission type, medication change, and disposition from the same table. Make clear that these are unadjusted encounter-level associations.

## Page 3 — Model Evaluation

Use `model_metrics.csv` as a table with ROC-AUC, precision, recall, F1-score, and PR-AUC. Insert the confusion-matrix image from `reports/model/` (or recreate from the reported matrix counts if adding those outputs). Label the fixed 0.5 threshold, grouped holdout, historical data, and unvalidated educational status. Model metrics are encounter-level and test patients do not overlap training patients.

Save the report as a `.pbix` locally. This repository contains source CSVs and instructions, not a verified PBIX artifact.

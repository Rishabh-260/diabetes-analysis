from pathlib import Path
import sqlite3
import pandas as pd

def refresh_database(df: pd.DataFrame, db_path: Path, sql_path: Path) -> None:
    db_path.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(db_path) as con:
        df.to_sql("encounters",con,if_exists="replace",index=False)
        queries=sql_path.read_text(encoding="utf-8").split(";")
        for query in queries:
            if query.strip(): pd.read_sql_query(query,con)

def export_powerbi(df: pd.DataFrame, metrics_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True,exist_ok=True)
    pd.DataFrame([{"total_encounters":len(df),"unique_patients":df.patient_nbr.nunique(),"early_readmissions":int(df.readmit_30d.sum()),"early_readmit_rate":df.readmit_30d.mean()}]).to_csv(out_dir/"executive_kpis.csv",index=False)
    for col in ["age_group","stay_group","prior_inpatient_group","medication_change","admission_type_id","primary_diagnosis_group"]:
        df.groupby(col,dropna=False).readmit_30d.agg(encounters="size",early_readmissions="sum",early_readmit_rate="mean").reset_index().to_csv(out_dir/f"by_{col}.csv",index=False)
    if metrics_path.exists(): pd.read_csv(metrics_path).to_csv(out_dir/"model_metrics.csv",index=False)
    df[["encounter_id","patient_nbr","readmit_30d","age_group","stay_group","prior_inpatient_group","medication_change","admission_type_id","primary_diagnosis_group","number_inpatient","time_in_hospital","discharge_disposition_id"]].to_csv(out_dir/"encounters_powerbi.csv",index=False)

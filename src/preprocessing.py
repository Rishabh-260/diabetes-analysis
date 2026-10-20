from pathlib import Path
import pandas as pd
from .data_loader import load_data

def _diagnosis_group(value: object) -> str:
    """Coarsen ICD-9 first diagnosis to broad descriptive buckets."""
    if pd.isna(value): return "Unknown"
    text = str(value).strip()
    if text.startswith(("V", "E")): return "Supplementary / external codes"
    try: code = int(float(text.split(".")[0]))
    except ValueError: return "Other / unclassified"
    if code == 250: return "Diabetes (250)"
    if 390 <= code <= 459 or code == 785: return "Circulatory"
    if 460 <= code <= 519 or code == 786: return "Respiratory"
    if 520 <= code <= 579 or code == 787: return "Digestive"
    if 800 <= code <= 999: return "Injury / poisoning"
    if 140 <= code <= 239: return "Neoplasms"
    if 240 <= code <= 279: return "Endocrine / metabolic"
    if 580 <= code <= 629 or code == 788: return "Genitourinary"
    if 290 <= code <= 319: return "Mental disorders"
    if 320 <= code <= 389: return "Nervous system"
    if 710 <= code <= 739: return "Musculoskeletal"
    if 680 <= code <= 709: return "Skin"
    if 1 <= code <= 139: return "Infectious / parasitic"
    return "Other ICD-9"

def prepare_data(raw_path: Path, out_dir: Path) -> tuple[pd.DataFrame, dict]:
    raw = load_data(raw_path)
    report = {"raw_rows": int(len(raw)), "raw_columns": int(raw.shape[1]), "unique_patients_raw": int(raw.patient_nbr.nunique()), "duplicate_rows": int(raw.duplicated().sum()), "missing_cells": int(raw.isna().sum().sum())}
    df = raw.drop_duplicates().copy()
    # Only the three documented readmission labels define the target; missing/other labels are excluded.
    valid = df.readmitted.isin(["<30", ">30", "NO"])
    report["invalid_target_rows_removed"] = int((~valid).sum())
    df = df.loc[valid].copy()
    df["readmit_30d"] = (df.readmitted == "<30").astype("int8")
    df["age_group"] = df.age.astype("string").fillna("Unknown")
    df["stay_group"] = pd.cut(pd.to_numeric(df.time_in_hospital, errors="coerce"), [0,2,5,8,14], labels=["1-2 days","3-5 days","6-8 days","9-14 days"], include_lowest=True).astype("string").fillna("Unknown")
    df["prior_inpatient_group"] = pd.cut(pd.to_numeric(df.number_inpatient, errors="coerce"), [-1,0,1,2,100], labels=["0","1","2","3+"], include_lowest=True).astype("string").fillna("Unknown")
    df["medication_change"] = df.change.map({"Ch":"Changed","No":"No change"}).fillna("Unknown")
    df["primary_diagnosis_group"] = df.diag_1.map(_diagnosis_group)
    # Dispositions for death/hospice make subsequent readmission structurally unlikely. Retain in primary data;
    # provide a flag so analysis can report a sensitivity cohort without silently discarding them.
    disposition = pd.to_numeric(df.discharge_disposition_id, errors="coerce")
    df["death_hospice_disposition"] = disposition.isin([11,13,14,19,20,21]).astype("int8")
    report["death_hospice_rows_retained"] = int(df.death_hospice_disposition.sum())
    report["clean_rows"] = int(len(df)); report["clean_columns"] = int(df.shape[1]); report["unique_patients_clean"] = int(df.patient_nbr.nunique())
    report["clean_missing_cells"] = int(df.isna().sum().sum())
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "cleaned_encounters.csv", index=False)
    (out_dir / "data_quality.json").write_text(__import__('json').dumps(report, indent=2), encoding="utf-8")
    df.isna().sum().sort_values(ascending=False).rename("missing_count").to_csv(out_dir / "missingness.csv")
    return df, report

def build_target(readmitted: pd.Series) -> pd.Series:
    mapping = {"<30": 1, ">30": 0, "NO": 0}
    return readmitted.map(mapping).astype("Int64")

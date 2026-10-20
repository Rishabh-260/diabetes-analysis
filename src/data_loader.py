from pathlib import Path
import zipfile
import requests
import pandas as pd

DATA_URL = "https://archive.ics.uci.edu/static/public/296/diabetes+130-us+hospitals+for+years+1999-2008.zip"
REQUIRED = {"encounter_id", "patient_nbr", "readmitted", "time_in_hospital", "discharge_disposition_id"}

def download_dataset(raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    csv_path = raw_dir / "diabetic_data.csv"
    if csv_path.exists() and csv_path.stat().st_size > 1000:
        return csv_path
    archive = raw_dir / "diabetes_uci.zip"
    if not archive.exists() or archive.stat().st_size < 1000 or not zipfile.is_zipfile(archive):
        response = requests.get(DATA_URL, timeout=(10, 90))
        response.raise_for_status()
        archive.write_bytes(response.content)
    if not zipfile.is_zipfile(archive):
        raise ValueError("UCI download was not a valid zip archive")
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        data_name = next(n for n in names if n.lower().endswith("diabetic_data.csv"))
        zf.extract(data_name, raw_dir)
        extracted = raw_dir / data_name
        if extracted != csv_path:
            extracted.replace(csv_path)
        mapping = next((n for n in names if n.lower().endswith("ids_mapping.csv")), None)
        if mapping:
            zf.extract(mapping, raw_dir)
            p = raw_dir / mapping
            if p != raw_dir / "IDS_mapping.csv": p.replace(raw_dir / "IDS_mapping.csv")
    return csv_path

def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, na_values=["?"], keep_default_na=True, low_memory=False)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {sorted(missing)}")
    return df

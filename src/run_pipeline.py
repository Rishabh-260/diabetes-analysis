from pathlib import Path
import json
import pandas as pd
from .data_loader import download_dataset
from .preprocessing import prepare_data
from .analysis import run_eda
from .modeling import train_evaluate
from .reporting import refresh_database, export_powerbi

ROOT=Path(__file__).resolve().parents[1]
def main():
    raw=download_dataset(ROOT/"data"/"raw")
    df,quality=prepare_data(raw,ROOT/"data"/"processed")
    eda=run_eda(df,ROOT/"reports")
    model=train_evaluate(df,ROOT/"reports"/"model")
    refresh_database(df,ROOT/"data"/"processed"/"diabetes_readmission.sqlite",ROOT/"sql"/"analysis_queries.sql")
    export_powerbi(df,ROOT/"reports"/"model"/"model_metrics.csv",ROOT/"dashboard"/"powerbi_data")
    summary={"quality":quality,"eda":eda,"model":model}
    (ROOT/"reports"/"execution_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()

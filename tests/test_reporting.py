import sqlite3
import pandas as pd
from src.reporting import refresh_database

def test_sql_database_and_queries(tmp_path):
    df=pd.DataFrame({"patient_nbr":[1,2],"readmit_30d":[1,0],"age_group":["a","b"],"stay_group":["1-2 days","3-5 days"],"prior_inpatient_group":["0","1"],"medication_change":["Changed","No change"],"admission_type_id":[1,2],"race":["A","B"],"death_hospice_disposition":[0,0]})
    sql=tmp_path/"q.sql"; sql.write_text("SELECT COUNT(*) AS n FROM encounters;",encoding="utf-8")
    db=tmp_path/"x.sqlite"; refresh_database(df,db,sql)
    with sqlite3.connect(db) as con: assert con.execute("SELECT COUNT(*) FROM encounters").fetchone()[0]==2

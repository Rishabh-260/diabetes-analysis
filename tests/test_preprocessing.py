import pandas as pd
import pytest
from src.preprocessing import build_target
from src.data_loader import load_data

def test_target_mapping_and_unknowns():
    got=build_target(pd.Series(["<30",">30","NO",None,"?"]))
    assert got.iloc[:3].tolist()==[1,0,0]
    assert pd.isna(got.iloc[3]) and pd.isna(got.iloc[4])

def test_question_mark_is_missing_and_required_columns_checked(tmp_path):
    p=tmp_path/"x.csv"
    pd.DataFrame({"encounter_id":[1],"patient_nbr":[2],"readmitted":["NO"],"time_in_hospital":[3],"discharge_disposition_id":[1],"race":["?"]}).to_csv(p,index=False)
    assert pd.isna(load_data(p).loc[0,"race"])
    pd.DataFrame({"x":[1]}).to_csv(p,index=False)
    with pytest.raises(ValueError): load_data(p)

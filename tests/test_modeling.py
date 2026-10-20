import pandas as pd
from src.modeling import model_features, train_evaluate

def test_identifier_and_target_leakage_excluded():
    df=pd.DataFrame({"encounter_id":[1],"patient_nbr":[2],"readmitted":["<30"],"readmit_30d":[1],"death_hospice_disposition":[0],"age":["[50-60)"],"value":[4]})
    assert set(model_features(df).columns)=={"age","value"}

def test_patient_grouped_split_and_metrics(tmp_path):
    rows=[]
    for p in range(50):
        for e in range(2): rows.append({"patient_nbr":p,"encounter_id":p*2+e,"readmitted":"NO","readmit_30d":int((p+e)%5==0),"age_group":"[50-60)","time_in_hospital":p%10+1,"change":"Ch" if p%2 else "No","number_inpatient":p%3,"discharge_disposition_id":1,"death_hospice_disposition":0})
    result=train_evaluate(pd.DataFrame(rows),tmp_path)
    assert result["split"]["train_patients"]+result["split"]["test_patients"]==50
    assert {"ROC-AUC","Precision","Recall","F1-score","PR-AUC"} <= set(result["metrics"][0])

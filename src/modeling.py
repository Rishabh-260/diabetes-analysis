from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score, f1_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import GroupShuffleSplit
import joblib

LEAKAGE = {"encounter_id", "patient_nbr", "readmitted", "readmit_30d", "death_hospice_disposition"}
def model_features(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=[c for c in LEAKAGE if c in df], errors="ignore")

def train_evaluate(df: pd.DataFrame, out_dir: Path, random_state: int=42) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    X=model_features(df); y=df.readmit_30d.astype(int); groups=df.patient_nbr
    splitter=GroupShuffleSplit(n_splits=1,test_size=.20,random_state=random_state)
    tr,te=next(splitter.split(X,y,groups))
    if set(groups.iloc[tr]) & set(groups.iloc[te]): raise AssertionError("patient leakage across split")
    numeric=X.select_dtypes(include=[np.number]).columns.tolist(); categorical=[c for c in X.columns if c not in numeric]
    num=Pipeline([("impute",SimpleImputer(strategy="median", add_indicator=True)),("scale",StandardScaler())])
    cat=Pipeline([("impute",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore",min_frequency=20))])
    prep=ColumnTransformer([("num",num,numeric),("cat",cat,categorical)], remainder="drop")
    models={"Logistic Regression":LogisticRegression(max_iter=1000,class_weight="balanced",solver="liblinear",random_state=random_state),"Random Forest":RandomForestClassifier(n_estimators=100,min_samples_leaf=10,class_weight="balanced_subsample",n_jobs=1,random_state=random_state)}
    results=[]; fitted={}
    for name, estimator in models.items():
        pipe=Pipeline([("preprocess",prep),("model",estimator)])
        pipe.fit(X.iloc[tr],y.iloc[tr]); prob=pipe.predict_proba(X.iloc[te])[:,1]; pred=(prob>=.5).astype(int)
        row={"model":name,"ROC-AUC":roc_auc_score(y.iloc[te],prob),"Precision":precision_score(y.iloc[te],pred,zero_division=0),"Recall":recall_score(y.iloc[te],pred,zero_division=0),"F1-score":f1_score(y.iloc[te],pred,zero_division=0),"PR-AUC":average_precision_score(y.iloc[te],prob),"test_encounters":len(te)}
        results.append(row); fitted[name]=(pipe,prob,pred)
    dummy=DummyClassifier(strategy="prior").fit(X.iloc[tr],y.iloc[tr]); dp=dummy.predict_proba(X.iloc[te])[:,1]
    results.append({"model":"Prevalence baseline","ROC-AUC":roc_auc_score(y.iloc[te],dp),"Precision":0.0,"Recall":0.0,"F1-score":0.0,"PR-AUC":average_precision_score(y.iloc[te],dp),"test_encounters":len(te)})
    pd.DataFrame(results).to_csv(out_dir/"model_metrics.csv",index=False)
    for name,(pipe,prob,pred) in fitted.items():
        cm=confusion_matrix(y.iloc[te],pred); disp=ConfusionMatrixDisplay(cm,display_labels=["No early readmit","Early readmit"]); disp.plot(cmap="Blues",values_format="d"); plt.title(f"{name} confusion matrix"); plt.tight_layout(); plt.savefig(out_dir/f"confusion_{name.lower().replace(' ','_')}.png",dpi=150); plt.close()
    # Select by ROC-AUC for a reproducible demonstration, preserving untouched patient-group test set.
    winner=max(fitted, key=lambda n: next(r["ROC-AUC"] for r in results if r["model"]==n))
    joblib.dump(fitted[winner][0],out_dir/"selected_model.joblib")
    pipe=fitted[winner][0]; model=pipe.named_steps["model"]; names=pipe.named_steps["preprocess"].get_feature_names_out()
    if hasattr(model,"coef_"): importance=pd.DataFrame({"feature":names,"coefficient":model.coef_[0]}).assign(abs_effect=lambda x:x.coefficient.abs()).sort_values("abs_effect",ascending=False)
    else: importance=pd.DataFrame({"feature":names,"importance":model.feature_importances_}).sort_values("importance",ascending=False)
    importance.head(30).to_csv(out_dir/"top_features.csv",index=False)
    summary={"split":"patient-grouped 80/20 holdout","random_state":random_state,"train_encounters":len(tr),"test_encounters":len(te),"train_patients":int(groups.iloc[tr].nunique()),"test_patients":int(groups.iloc[te].nunique()),"selected_model":winner,"test_positive_rate":float(y.iloc[te].mean())}
    (out_dir/"split_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    return {"metrics":results,"split":summary}

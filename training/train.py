from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier


from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix


@dataclass
class TrainResult:
    model_name: str
    metrics: dict[str, float]
    artifact_path: Path


def build_model_pipeline(model_name: str, available_columns: list[str]):
    # Definir dinámicamente las variables según disponibilidad
    categorical_candidates = ["tipo_delito", "barrio", "comuna", "zona_tipo", "mes", "dia_semana", "hora"]
    numeric_candidates = ["densidad_eventos_30d", "tasa_crimen_1000", "poblacion_total", "movilidad_intensidad"]
    
    categorical = [c for c in categorical_candidates if c in available_columns]
    numeric = [c for c in numeric_candidates if c in available_columns]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                              ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
        ],
        remainder="drop",
    )

    models = {
        "logistic": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "dt": DecisionTreeClassifier(max_depth=10, random_state=42, class_weight="balanced"),
        "rf": RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced"),
        "gb": GradientBoostingClassifier(random_state=42),
        "xgb": XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=42,
        ),
    }
    return Pipeline([("preprocess", preprocessor), ("model", models[model_name])])



def train_classification(df: pd.DataFrame, target_col: str, output_dir: Path) -> list[TrainResult]:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = df.copy()
    
    # Asegurar nulos llenos antes del split
    data = data.dropna(subset=[target_col])
    y = data[target_col].astype(int)
    X = data.drop(columns=[target_col])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    results: list[TrainResult] = []
    # Usamos 'logistic', 'dt', 'rf', 'xgb' para entrenamiento veloz y eficiente
    for model_name in ("logistic", "dt", "rf", "xgb"):
        pipeline = build_model_pipeline(model_name, list(X_train.columns))
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]
        
        cm = confusion_matrix(y_test, y_pred)
        
        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, y_prob)),
            "confusion_matrix": {
                "tn": int(cm[0, 0]),
                "fp": int(cm[0, 1]),
                "fn": int(cm[1, 0]),
                "tp": int(cm[1, 1])
            }
        }
        artifact_path = output_dir / f"{model_name}.joblib"
        joblib.dump(pipeline, artifact_path)
        with open(output_dir / f"{model_name}.metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        results.append(TrainResult(model_name, metrics, artifact_path))
    return results




def main():
    # Encontrar dataset procesado (preferimos el nacional)
    project_root = Path(__file__).resolve().parents[1]
    
    crime_path = project_root / "datasets" / "processed" / "crime_hurtos_nacional.parquet"
    is_nacional = True
    
    if not crime_path.exists():
        crime_path = project_root / "datasets" / "processed" / "crime_bga.parquet"
        is_nacional = False
        
    pop_path = project_root / "datasets" / "processed" / "poblacion_bga.parquet"
    acc_path = project_root / "datasets" / "processed" / "accidentes_bga.parquet"
    
    if crime_path.exists():
        from preprocessing.features import build_full_ml_features
        crime_df = pd.read_parquet(crime_path)
        pop_df = pd.read_parquet(pop_path) if pop_path.exists() else pd.DataFrame()
        acc_df = pd.read_parquet(acc_path) if acc_path.exists() else pd.DataFrame()
        
        # Generar características a escala colombiana
        featured_df = build_full_ml_features(crime_df, pop_df, acc_df, is_nacional=is_nacional)
        
        output_dir = project_root / "models"
        print("Entrenando modelos clasificadores de riesgo delictivo...")
        results = train_classification(featured_df, "es_riesgo_alto", output_dir)
        for r in results:
            print(f"Modelo: {r.model_name.upper()} | F1-Score: {r.metrics['f1']:.4f} | ROC-AUC: {r.metrics['roc_auc']:.4f}")
            
        # Hotspots
        print("Generando agrupamiento espacial de hotspots delictivos...")
        from training.hotspots import detect_hotspots_dbscan
        db_model, db_df = detect_hotspots_dbscan(featured_df, eps_km=1.5 if is_nacional else 0.5, min_samples=10)
        joblib.dump(db_model, output_dir / "dbscan_hotspots.joblib")
        db_df.to_parquet(project_root / "datasets" / "processed" / "crime_bga_featured.parquet", index=False)
        print("Entrenamiento completado de forma exitosa.")
    else:
        print("Error: No se encontró ningún dataset procesado de criminalidad.")


if __name__ == "__main__":
    main()



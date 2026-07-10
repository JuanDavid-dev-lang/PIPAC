import sys
from pathlib import Path
import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from modules.latest_reports.ml.feature_store import FeatureStore

def train_national_model():
    print("Loading processed data...")
    processed_dir = PROJECT_ROOT / 'datasets' / 'processed'
    # For now, we will use hurtos_modalidades if it exists
    data_path = processed_dir / 'hurtos_modalidades.parquet'
    
    if not data_path.exists():
        print(f"Data file {data_path} not found. Ensure ETL runs first.")
        return
        
    df = pd.read_parquet(data_path)
    
    print(f"Loaded {len(df)} rows. Building features...")
    fs = FeatureStore(PROJECT_ROOT)
    featured_df = fs.build_features(df)
    
    fs.save_featured(featured_df, 'hurtos_modalidades_featured')
    
    print("Preparing data for training...")
    # Features for the model
    features = ['mes', 'dia_semana', 'hora', 'es_fin_semana', 'es_nocturno', 'densidad_eventos_historico']
    target = 'es_riesgo_alto'
    
    model_df = featured_df.dropna(subset=features + [target]).copy()
    
    if model_df.empty:
        print("Not enough data to train.")
        return
        
    X = model_df[features].astype(float)
    y = model_df[target].astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training XGBoost Classifier...")
    model = XGBClassifier(
        n_estimators=50, 
        learning_rate=0.1, 
        max_depth=4, 
        random_state=42,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Model Accuracy: {acc:.4f}")
    
    # Save the model
    models_dir = PROJECT_ROOT / 'models'
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / 'national_risk_model.joblib'
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_national_model()

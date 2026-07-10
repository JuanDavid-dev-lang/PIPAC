import pandas as pd
from pathlib import Path

class FeatureStore:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.featured_dir = self.project_root / 'datasets' / 'featured'
        self.featured_dir.mkdir(parents=True, exist_ok=True)
        
    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
            
        df = df.copy()
        
        # Temporal features
        if 'fecha_parsed' in df.columns:
            df['es_fin_semana'] = df['fecha_parsed'].dt.dayofweek >= 5
            df['trimestre'] = df['fecha_parsed'].dt.quarter
        
        if 'hora' in df.columns:
            df['es_nocturno'] = (df['hora'] >= 18) | (df['hora'] < 6)
            df['es_hora_pico'] = ((df['hora'] >= 6) & (df['hora'] <= 8)) | ((df['hora'] >= 17) & (df['hora'] <= 19))
            
        # Territorial density features (mocking an aggregation over the last 30d equivalent)
        if 'municipio' in df.columns:
            # Densidad de eventos (count per municipio)
            municipio_counts = df['municipio'].value_counts()
            df['densidad_eventos_historico'] = df['municipio'].map(municipio_counts).fillna(0)
            
            # Simple risk score based on density
            max_dens = df['densidad_eventos_historico'].max()
            if pd.notna(max_dens) and max_dens > 0:
                df['risk_score'] = df['densidad_eventos_historico'] / max_dens
            else:
                df['risk_score'] = 0.0
                
            df['es_riesgo_alto'] = (df['risk_score'] > 0.7).astype(int)
            
        return df

    def save_featured(self, df: pd.DataFrame, name: str):
        path = self.featured_dir / f"{name}.parquet"
        df.to_parquet(path, index=False)
        return path

import pandas as pd
import numpy as np

class DataCleaner:
    def clean(self, df: pd.DataFrame, dataset_key: str) -> pd.DataFrame:
        if df.empty:
            return df
        
        df = df.copy()
        
        # Determine the date column
        date_cols_candidates = ['fecha_hecho', 'fecha']
        date_col = next((c for c in date_cols_candidates if c in df.columns), None)
        
        if date_col:
            # Parse dates
            df['fecha_parsed'] = pd.to_datetime(df[date_col], errors='coerce')
            df['anio'] = df['fecha_parsed'].dt.year
            df['mes'] = df['fecha_parsed'].dt.month
            df['dia'] = df['fecha_parsed'].dt.day
            df['dia_semana'] = df['fecha_parsed'].dt.dayofweek
            
            # Hora
            hora_cols_candidates = ['hora_hecho', 'hora']
            hora_col = next((c for c in hora_cols_candidates if c in df.columns), None)
            if hora_col:
                # Extract first two digits or use full string for hour
                df['hora'] = pd.to_numeric(df[hora_col].astype(str).str.extract(r'(\d{1,2})')[0], errors='coerce').fillna(0).astype(int)
            else:
                df['hora'] = df['fecha_parsed'].dt.hour
                
        # String normalization
        string_cols = df.select_dtypes(include=['object', 'string']).columns
        for col in string_cols:
            df[col] = df[col].astype(str).str.upper().str.strip()
            
        # Coordinates validation
        if 'latitud' in df.columns and 'longitud' in df.columns:
            df['lat'] = pd.to_numeric(df['latitud'], errors='coerce')
            df['lon'] = pd.to_numeric(df['longitud'], errors='coerce')
            
            # Valid range for Colombia approx: lat -4 to 13, lon -80 to -66
            valid_lat = (df['lat'] >= -4) & (df['lat'] <= 13)
            valid_lon = (df['lon'] >= -80) & (df['lon'] <= -66)
            
            df.loc[~valid_lat, 'lat'] = np.nan
            df.loc[~valid_lon, 'lon'] = np.nan
            
        # Normalize age
        edad_cols = ['edad']
        edad_col = next((c for c in edad_cols if c in df.columns), None)
        if edad_col:
            df['edad'] = pd.to_numeric(df[edad_col], errors='coerce')
            df.loc[(df['edad'] < 0) | (df['edad'] > 120), 'edad'] = np.nan
            
            # Grupo etario
            conditions = [
                (df['edad'] < 18),
                (df['edad'] >= 18) & (df['edad'] < 30),
                (df['edad'] >= 30) & (df['edad'] < 60),
                (df['edad'] >= 60)
            ]
            choices = ['MENOR', 'JOVEN', 'ADULTO', 'ADULTO MAYOR']
            df['grupo_etario'] = np.select(conditions, choices, default='N/D')
        
        # Sexo
        sexo_cols = ['sexo', 'genero']
        sexo_col = next((c for c in sexo_cols if c in df.columns), None)
        if sexo_col:
            df['sexo'] = df[sexo_col].map({'MASCULINO': 'M', 'FEMENINO': 'F', 'M': 'M', 'F': 'F'}).fillna('N/D')

        return df

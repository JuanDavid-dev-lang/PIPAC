from __future__ import annotations

import numpy as np
import pandas as pd


def build_temporal_features(df: pd.DataFrame, date_col: str = "fecha_hora") -> pd.DataFrame:
    data = df.copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data["anio"] = data[date_col].dt.year
    data["mes"] = data[date_col].dt.month
    data["dia"] = data[date_col].dt.day
    data["dia_semana"] = data[date_col].dt.dayofweek
    data["hora"] = data[date_col].dt.hour
    data["semana_anio"] = data[date_col].dt.isocalendar().week.astype("Int64")
    data["es_fin_de_semana"] = data["dia_semana"].isin([5, 6]).astype(int)
    return data


def add_crime_rates(df: pd.DataFrame, count_col: str = "conteo", pop_col: str = "poblacion_total") -> pd.DataFrame:
    data = df.copy()
    # Evitar divisiones por cero o nulos
    data["tasa_crimen_1000"] = (data[count_col].fillna(0) / data[pop_col].fillna(1)).fillna(0) * 1000
    return data


def add_rolling_density(df: pd.DataFrame, group_col: str, count_col: str = "conteo") -> pd.DataFrame:
    data = df.sort_values(["fecha_hora"]).copy()
    
    # Calcular densidad acumulando conteos por fecha
    # Agrupamos por barrio y aplicamos rolling sobre una ventana de 30 días basada en la fecha
    # Una aproximación robusta que evita reindexación con duplicados es calcular de manera explícita:
    densities = []
    for barrio, group in data.groupby(group_col):
        group_sorted = group.sort_values("fecha_hora")
        # Establecemos índice temporal de fecha_hora para usar .rolling('30D')
        rolling_series = group_sorted.set_index("fecha_hora")[count_col].rolling("30D").sum()
        # Mapeamos de vuelta al índice original del dataframe ordenado
        rolling_series.index = group_sorted.index
        densities.append(rolling_series)
        
    if densities:
        data["densidad_eventos_30d"] = pd.concat(densities).sort_index()
    else:
        data["densidad_eventos_30d"] = 1.0
        
    return data



def build_full_ml_features(crime_df: pd.DataFrame, pop_df: pd.DataFrame, acc_df: pd.DataFrame, is_nacional: bool = False) -> pd.DataFrame:
    """
    Integra las características temporales, geográficas y tasas de criminalidad
    cruzando delitos, poblaciones territoriales y datos de accidentes proxy.
    Soporta datasets locales de Bucaramanga y datasets a nivel país (Colombia).
    """
    df = crime_df.copy()
    
    # Estandarizar barrios/municipios en mayúsculas
    df["barrio"] = df["barrio"].astype(str).str.upper().str.strip()
    
    # 1. Cruzar con poblaciones por territorio para obtener tasa_crimen_1000
    if not is_nacional and not pop_df.empty:
        # Bucaramanga específico
        pop_clean = pop_df.copy()
        pop_clean["personas"] = pd.to_numeric(pop_clean["personas"], errors="coerce").fillna(0)
        pop_clean["barrio_poligono"] = pop_clean["barrio_poligono"].astype(str).str.upper().str.strip()
        pop_group = pop_clean.groupby("barrio_poligono")["personas"].sum().reset_index()
        pop_group = pop_group.rename(columns={"barrio_poligono": "barrio", "personas": "poblacion_total"})
        df = df.merge(pop_group, on="barrio", how="left")
    else:
        # Nacional o sin tabla de población: usamos fallbacks proporcionales
        df["poblacion_total"] = 50000.0  # fallback promedio por municipio
        
    df["poblacion_total"] = pd.to_numeric(df["poblacion_total"], errors="coerce").fillna(50000.0)
    # Evitar poblaciones de cero para prevenir división por cero
    df.loc[df["poblacion_total"] <= 0, "poblacion_total"] = 50000.0
    df = add_crime_rates(df, "conteo", "poblacion_total")

    # 2. Agregar rolling density de eventos a 30 días
    df = add_rolling_density(df, "barrio", "conteo")
    
    # 3. Cruzar accidentes como proxy de movilidad
    if not is_nacional and not acc_df.empty:
        acc_clean = acc_df.copy()
        acc_clean["barrio"] = acc_clean["barrio"].astype(str).str.upper().str.strip()
        acc_count = acc_clean.groupby("barrio").size().reset_index(name="movilidad_intensidad")
        df = df.merge(acc_count, on="barrio", how="left")
    else:
        df["movilidad_intensidad"] = 0.0
        
    df["movilidad_intensidad"] = df["movilidad_intensidad"].fillna(0.0)
    
    # 4. Generar variable objetivo de riesgo basada en la mediana de densidad_eventos_30d
    median_val = df["densidad_eventos_30d"].median()
    if median_val == df["densidad_eventos_30d"].min():
        median_val = df["densidad_eventos_30d"].mean()
        
    df["es_riesgo_alto"] = (df["densidad_eventos_30d"] > median_val).astype(int)
    
    # Asignar coordenadas geográficas reales o simuladas para el mapa interactivo
    if is_nacional:
        df = simulate_national_coordinates(df)
    
    return df


def simulate_national_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Asigna coordenadas aproximadas de los departamentos principales de Colombia para el mapa.
    """
    data = df.copy()
    
    # Centroides aproximados de departamentos en Colombia
    dept_coords = {
        "ANTIOQUIA": (6.244, -75.581),
        "BOGOTA": (4.711, -74.072),
        "VALLE": (3.437, -76.522),
        "ATLANTICO": (10.963, -74.796),
        "SANTANDER": (7.119, -73.116),
        "CUNDINAMARCA": (4.609, -74.081),
        "BOLIVAR": (10.399, -75.514),
        "NARIÑO": (1.213, -77.281),
        "CORDOBA": (8.747, -75.881),
        "HUILA": (2.927, -75.281),
        "TOLIMA": (4.438, -75.232),
        "BOYACA": (5.535, -73.367),
        "CALDAS": (5.068, -75.517),
        "RISARALDA": (4.813, -75.696),
        "META": (4.142, -73.626),
        "NORTE DE SANTANDER": (7.893, -72.507),
        "QUINDIO": (4.533, -75.681),
        "CESAR": (10.463, -73.253),
        "MAGDALENA": (11.240, -74.199),
        "SUCRE": (9.304, -75.397),
        "CAUCA": (2.441, -76.613),
        "CHOCO": (5.691, -76.658),
        "GUAJIRA": (11.544, -72.906),
        "CASANARE": (5.337, -72.395),
        "PUTUMAYO": (1.149, -76.646),
        "ARAUCA": (7.084, -70.759),
        "CAQUETA": (1.614, -75.606),
        "GUAVIARE": (2.566, -72.641),
        "VICHADA": (6.188, -67.484),
        "AMAZONAS": (-1.446, -69.940),
        "VAUPES": (1.251, -70.173),
        "GUAINIA": (3.865, -67.923),
    }
    
    default_lat, default_lon = 4.570, -74.297 # Centro geográfico de Colombia
    
    lats = []
    lons = []
    
    for dept in data["comuna"].fillna("SANTANDER").astype(str).str.upper().str.strip():
        matched = False
        for key, coords in dept_coords.items():
            if key in dept or dept in key:
                lat = coords[0] + np.random.normal(0, 0.15) # Mayor dispersión para municipios
                lon = coords[1] + np.random.normal(0, 0.15)
                lats.append(lat)
                lons.append(lon)
                matched = True
                break
        if not matched:
            lat = default_lat + np.random.normal(0, 0.5)
            lon = default_lon + np.random.normal(0, 0.5)
            lats.append(lat)
            lons.append(lon)
            
    data["lat"] = lats
    data["lon"] = lons
    return data



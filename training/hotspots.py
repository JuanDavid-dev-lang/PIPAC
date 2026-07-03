from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
import joblib


def detect_hotspots_kmeans(df: pd.DataFrame, n_clusters: int = 5) -> tuple[KMeans, pd.DataFrame]:
    """
    Agrupa los delitos usando KMeans para encontrar centros de patrullaje óptimos.
    """
    # Extraer coordenadas. Si no existen, simulamos para Bucaramanga
    coords = df.copy()
    if "lat" not in coords.columns or "lon" not in coords.columns:
        # Generar coordenadas simuladas dentro de Bucaramanga para los barrios
        coords = simulate_geographic_coordinates(coords)
        
    X = coords[["lat", "lon"]].dropna()
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(X)
    
    coords["cluster_kmeans"] = kmeans.labels_
    return kmeans, coords


def detect_hotspots_dbscan(df: pd.DataFrame, eps_km: float = 0.5, min_samples: int = 10) -> tuple[DBSCAN, pd.DataFrame]:
    """
    Agrupa los delitos usando DBSCAN para encontrar clusters de densidad variable.
    Usa la distancia de Haversine para precisión de kilómetros en esfera terrestre.
    """
    coords = df.copy()
    if "lat" not in coords.columns or "lon" not in coords.columns:
        coords = simulate_geographic_coordinates(coords)
        
    X = coords[["lat", "lon"]].dropna()
    
    # Convertir eps de km a radianes
    kms_per_radian = 6371.0088
    epsilon = eps_km / kms_per_radian
    
    db = DBSCAN(eps=epsilon, min_samples=min_samples, metric="haversine", algorithm="ball_tree")
    
    # DBSCAN en haversine requiere radianes: [lat_rad, lon_rad]
    coords_rad = np.radians(X)
    db.fit(coords_rad)
    
    coords["cluster_dbscan"] = db.labels_
    return db, coords


def simulate_geographic_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Simulador robusto de coordenadas espaciales para Bucaramanga basado en barrios conocidos.
    """
    data = df.copy()
    
    # Diccionario de centroides conocidos de Bucaramanga
    centroids = {
        "CENTRO": (7.119, -73.122),
        "CABECERA": (7.113, -73.116),
        "MORRORICO": (7.108, -73.104),
        "GIRARDOT": (7.126, -73.110),
        "PROVENZA": (7.097, -73.091),
        "MUTIS": (7.105, -73.125),
        "SAN ALONSO": (7.124, -73.114),
        "ALARCÓN": (7.122, -73.120),
        "REAL DE MINAS": (7.106, -73.128),
        "COLORADOS": (7.170, -73.130),
    }
    
    default_lat, default_lon = 7.119, -73.116
    
    lats = []
    lons = []
    
    for barrio in data["barrio"].fillna("CENTRO").astype(str).str.upper().str.strip():
        # Buscar coincidencia o aproximada
        matched = False
        for key, coords in centroids.items():
            if key in barrio or barrio in key:
                # Agregar pequeño ruido gaussiano para simular eventos individuales
                lat = coords[0] + np.random.normal(0, 0.003)
                lon = coords[1] + np.random.normal(0, 0.003)
                lats.append(lat)
                lons.append(lon)
                matched = True
                break
        if not matched:
            lat = default_lat + np.random.normal(0, 0.01)
            lon = default_lon + np.random.normal(0, 0.01)
            lats.append(lat)
            lons.append(lon)
            
    data["lat"] = lats
    data["lon"] = lons
    return data

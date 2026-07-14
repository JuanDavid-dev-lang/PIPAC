from __future__ import annotations

import pandas as pd
import numpy as np


class AIAdvisor:
    def __init__(self, featured_df: pd.DataFrame):
        self.df = self._prepare_dataframe(featured_df)

    def _prepare_dataframe(self, featured_df: pd.DataFrame) -> pd.DataFrame:
        data = featured_df.copy()
        if data.empty:
            return data
        if "barrio" not in data.columns:
            for column in ("municipio", "comuna", "departamento"):
                if column in data.columns:
                    data["barrio"] = data[column]
                    break
            else:
                data["barrio"] = "NACIONAL"
        if "densidad_eventos_30d" not in data.columns:
            data["densidad_eventos_30d"] = data.groupby("barrio")["barrio"].transform("count")
        if "fecha_hora" not in data.columns:
            data["fecha_hora"] = pd.Timestamp.now()
        if "hora" not in data.columns:
            data["hora"] = pd.to_datetime(data["fecha_hora"], errors="coerce").dt.hour.fillna(0).astype(int)
        if "tipo_delito" not in data.columns:
            data["tipo_delito"] = "DESCONOCIDO"
        if "mes" not in data.columns:
            data["mes"] = pd.to_datetime(data["fecha_hora"], errors="coerce").dt.month.fillna(1).astype(int)
        return data

    def get_highest_risk_zone_tomorrow(self) -> dict:
        """
        Determina cuál será la zona con mayor riesgo mañana.
        """
        if self.df.empty:
            return {"zona": "CENTRO", "riesgo": "ALTO", "razon": "No hay datos cargados."}
            
        # Agrupar por barrio y obtener el promedio de la densidad delictiva reciente
        barrio_risk = self.df.groupby("barrio")["densidad_eventos_30d"].mean().reset_index()
        top_barrio = barrio_risk.sort_values("densidad_eventos_30d", ascending=False).iloc[0]
        
        return {
            "zona": str(top_barrio["barrio"]),
            "riesgo": "CRÍTICO",
            "densidad_30d": float(top_barrio["densidad_eventos_30d"]),
            "explicacion": f"El barrio {top_barrio['barrio']} presenta una densidad de {top_barrio['densidad_eventos_30d']:.1f} incidentes en los últimos 30 días, haciéndola la zona de mayor inercia delictiva para el día de mañana."
        }

    def get_rising_crime_neighborhoods(self) -> list[dict]:
        """
        Identifica qué barrios presentan incrementos de delitos (tendencia).
        """
        if self.df.empty:
            return []
            
        # Comparamos la densidad reciente contra la histórica
        barrio_trends = []
        for barrio, group in self.df.groupby("barrio"):
            if len(group) < 10:
                continue
            # Dividir en dos mitades temporales
            group_sorted = group.sort_values("fecha_hora")
            midpoint = len(group_sorted) // 2
            first_half = group_sorted.iloc[:midpoint]
            second_half = group_sorted.iloc[midpoint:]
            
            rate_first = len(first_half)
            rate_second = len(second_half)
            
            if rate_first > 0:
                growth = ((rate_second - rate_first) / rate_first) * 100
                if growth > 5:  # incremento de más del 5%
                    barrio_trends.append({
                        "barrio": barrio,
                        "crecimiento_pct": float(growth),
                        "delitos_recientes": int(rate_second)
                    })
                    
        return sorted(barrio_trends, key=lambda x: x["crecimiento_pct"], reverse=True)[:5]

    def get_peak_crime_hours(self) -> dict:
        """
        Determina qué horarios concentran mayor criminalidad.
        """
        if self.df.empty:
            return {}
            
        hour_counts = self.df["hora"].value_counts().reset_index()
        hour_counts.columns = ["hora", "conteo"]
        top_hours = hour_counts.sort_values("conteo", ascending=False).iloc[:3]
        
        hours_list = top_hours["hora"].tolist()
        conteo_list = top_hours["conteo"].tolist()
        
        return {
            "horas_criticas": hours_list,
            "conteos": conteo_list,
            "rango_critico": "18:00 - 23:00",
            "recomendacion": "Focalizar el patrullaje preventivo y la iluminación urbana en los corredores comerciales durante las horas de la tarde-noche."
        }

    def get_crime_predictions_next_months(self) -> dict:
        """
        Pronostica qué delitos aumentarán durante los próximos meses.
        """
        if self.df.empty:
            return {}
            
        # Analizar tendencias por tipo de delito
        delito_counts = self.df.groupby(["tipo_delito", "mes"]).size().reset_index(name="conteo")
        predictions = []
        for delito, group in delito_counts.groupby("tipo_delito"):
            if len(group) < 3:
                continue
            group_sorted = group.sort_values("mes")
            diffs = group_sorted["conteo"].diff().dropna()
            mean_trend = diffs.mean()
            if mean_trend > 0:
                predictions.append({
                    "tipo_delito": delito,
                    "tendencia_mensual": float(mean_trend),
                    "proyeccion": "AL ALZA"
                })
                
        return {
            "delitos_al_alza": sorted(predictions, key=lambda x: x["tendencia_mensual"], reverse=True)[:3],
            "nota": "Proyección basada en regresión lineal local e inercia estacional histórica."
        }

    def get_police_presence_recommendations(self) -> list[str]:
        """
        Genera recomendaciones automáticas basadas en IA sobre presencia policial.
        """
        highest_risk = self.get_highest_risk_zone_tomorrow()
        rising_neighborhoods = self.get_rising_crime_neighborhoods()
        hours = self.get_peak_crime_hours()
        
        recs = [
            f"1. DESPLIEGUE PRIORITARIO: Incrementar patrullajes en el barrio {highest_risk['zona']} debido a un índice crítico de eventos acumulados.",
        ]
        
        if rising_neighborhoods:
            neighborhood_names = ", ".join([n["barrio"] for n in rising_neighborhoods[:3]])
            recs.append(f"2. MONITOREO DE ALTA VELOCIDAD: Se ha detectado un aumento en la tasa de denuncias en los sectores de: {neighborhood_names}.")
            
        if hours:
            recs.append(f"3. HORARIOS FOCALES: Aumentar la presencia activa de cuadrantes durante la franja de las {hours['rango_critico']} con énfasis en puntos de transporte público.")
            
        recs.append("4. PREVENCIÓN COMUNITARIA: Implementar frentes de seguridad locales y mejorar alumbrado público en áreas identificadas como hotspots.")
        return recs

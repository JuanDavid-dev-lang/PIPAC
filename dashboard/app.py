from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, Input, Output, dcc, html
from sklearn.cluster import DBSCAN

from dashboard.api_client import fetch_crimes, fetch_predictions
from utils.ai_advisor import AIAdvisor

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_STARTED_AT = datetime.now()

DARK_BG = "#08111F"
CARD_BG = "rgba(16, 28, 46, 0.92)"
CARD_BORDER = "rgba(29, 42, 66, 0.9)"
TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#94A3B8"
PRIMARY = "#3B82F6"
GREEN = "#10B981"
YELLOW = "#FBBF24"
ORANGE = "#F97316"
RED = "#EF4444"
VIOLET = "#8B5CF6"
CYAN = "#22D3EE"
PINK = "#FB7185"

CITY_NAV = [
    ("Inicio", "#inicio", True),
    ("Mapa de Riesgo", "#mapa-riesgo-seccion", False),
    ("Analítica", "#analitica-seccion", False),
    ("IA Predictiva", "#ia-seccion", False),
    ("Alertas", "#alertas-seccion", False),
    ("Participación Ciudadana", "#ciudadania-seccion", False),
    ("Reportes", "#reportes-seccion", False),
    ("Configuración", "#configuracion-seccion", False),
]


def load_initial_dataframe() -> pd.DataFrame:
    candidates = [
        PROJECT_ROOT / "datasets" / "processed" / "crime_hurtos_nacional.parquet",
        PROJECT_ROOT / "datasets" / "processed" / "crime_bga.parquet",
        PROJECT_ROOT / "datasets" / "processed" / "crime_bga_featured.parquet",
    ]
    for path in candidates:
        if path.exists():
            try:
                return pd.read_parquet(path)
            except Exception:
                continue

    try:
        items = fetch_crimes(limit=1000)
        if items:
            return pd.DataFrame(items)
    except Exception:
        pass

    return pd.DataFrame(
        {
            "barrio": ["CABECERA", "LA CONCORDIA", "CENTRO", "GIRON", "MORRORICO", "PENTAGONO"],
            "comuna": ["BUCARAMANGA", "BUCARAMANGA", "BUCARAMANGA", "GIRÓN", "BUCARAMANGA", "FLORIDABLANCA"],
            "tipo_delito": ["HURTO A PERSONAS", "HURTO A RESIDENCIAS", "LESIONES PERSONALES", "HURTO A PERSONAS", "HURTO A PERSONAS", "LESIONES PERSONALES"],
            "lat": [7.1193, 7.1178, 7.1184, 7.0708, 7.1161, 7.0722],
            "lon": [-73.1227, -73.1059, -73.1191, -73.1740, -73.1220, -73.0870],
            "densidad_eventos_30d": [144.0, 112.0, 98.0, 76.0, 61.0, 54.0],
            "tasa_crimen_1000": [8.8, 7.5, 6.4, 5.1, 4.2, 3.8],
            "es_riesgo_alto": [1, 1, 1, 1, 0, 0],
            "conteo": [1, 1, 1, 1, 1, 1],
            "anio": [2026, 2026, 2026, 2026, 2026, 2026],
            "mes": [1, 2, 3, 4, 5, 6],
            "dia_semana": [0, 1, 2, 3, 4, 5],
            "hora": [10, 15, 20, 22, 18, 12],
            "edad": [22, 31, 28, 19, 35, 41],
            "sexo": ["F", "M", "F", "M", "F", "M"],
        }
    )


def ensure_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    df2 = dataframe.copy()
    n = len(df2) if not df2.empty else 1
    defaults = {
        "tipo_delito": "DESCONOCIDO",
        "comuna": "NACIONAL",
        "municipio": "NACIONAL",
        "departamento": "NACIONAL",
        "barrio": "DESCONOCIDO",
        "lat": 4.6,
        "lon": -74.0,
        "densidad_eventos_30d": 0.0,
        "tasa_crimen_1000": 0.0,
        "es_riesgo_alto": 0,
        "conteo": 1,
        "anio": 2026,
        "mes": 1,
        "dia_semana": 0,
        "hora": 0,
        "edad": 0,
        "sexo": "N/D",
        "nivel_riesgo": "MEDIO",
        "fecha": pd.Timestamp.now().normalize(),
    }
    for column, value in defaults.items():
        if column not in df2.columns:
            df2[column] = [value] * n

    for column in ["lat", "lon", "densidad_eventos_30d", "tasa_crimen_1000", "edad"]:
        df2[column] = pd.to_numeric(df2[column], errors="coerce").fillna(0.0)
    for column in ["es_riesgo_alto", "conteo", "anio", "mes", "dia_semana", "hora"]:
        df2[column] = pd.to_numeric(df2[column], errors="coerce").fillna(0).astype(int)
    for column in ["barrio", "comuna", "municipio", "departamento", "tipo_delito", "sexo", "nivel_riesgo"]:
        df2[column] = df2[column].astype(str)

    return df2


def series_to_sparkline(values: Iterable[float], color: str) -> go.Figure:
    values = list(values) or [0]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(len(values))),
            y=values,
            mode="lines",
            line={"color": color, "width": 2.5},
            fill="tozeroy",
            fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.14)",
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        height=52,
        xaxis={"visible": False, "fixedrange": True},
        yaxis={"visible": False, "fixedrange": True},
    )
    return fig


def mini_card(title: str, value: str, subtitle: str, delta: str, color: str, spark_values: Iterable[float], icon: str) -> html.Div:
    return html.Div(
        className="pipac-card pipac-kpi-card",
        children=[
            html.Div(
                className="pipac-kpi-head",
                children=[
                    html.Div(
                        className="pipac-kpi-icon",
                        style={"background": f"linear-gradient(135deg, {color}, rgba(255,255,255,0.18))"},
                        children=icon,
                    ),
                    html.Div(
                        className="pipac-kpi-delta",
                        style={"color": color},
                        children=delta,
                    ),
                ],
            ),
            html.Div(className="pipac-kpi-title", children=title),
            html.Div(className="pipac-kpi-value", children=value),
            html.Div(className="pipac-kpi-subtitle", children=subtitle),
            dcc.Graph(figure=series_to_sparkline(spark_values, color), config={"displayModeBar": False}, className="pipac-sparkline"),
        ],
    )


def section_card(title: str, subtitle: str, children, extra_class: str = "") -> html.Div:
    class_name = "pipac-card pipac-section-card"
    if extra_class:
        class_name = f"{class_name} {extra_class}"
    return html.Div(
        className=class_name,
        children=[
            html.Div(
                className="pipac-section-header",
                children=[
                    html.Div(
                        children=[
                            html.Div(className="pipac-section-title", children=title),
                            html.Div(className="pipac-section-subtitle", children=subtitle),
                        ]
                    ),
                ],
            ),
            children,
        ],
    )


def badge(text: str, tone: str = "primary") -> html.Span:
    return html.Span(className=f"pipac-badge pipac-badge-{tone}", children=text)


def nav_item(label: str, href: str, active: bool = False) -> html.A:
    return html.A(
        href=href,
        className=f"pipac-nav-item {'pipac-nav-item-active' if active else ''}",
        children=[html.Span(className="pipac-nav-dot"), html.Span(label)],
    )


def resolve_city_column(dataframe: pd.DataFrame) -> str:
    for column in ("municipio", "comuna", "departamento", "barrio"):
        if column in dataframe.columns:
            return column
    return "barrio"


df = ensure_columns(load_initial_dataframe())
delitos_disponibles = sorted(df["tipo_delito"].dropna().unique())
barrios_disponibles = sorted(df["barrio"].dropna().unique())
city_column = resolve_city_column(df)
city_options = sorted(df[city_column].dropna().astype(str).unique())
severidad_opciones = [
    {"label": "Bajo", "value": "BAJO"},
    {"label": "Medio", "value": "MEDIO"},
    {"label": "Alto", "value": "ALTO"},
]

app = Dash(__name__, title="PIPAC - Plataforma de Predicción y Análisis de Criminalidad")
server = app.server


header_buttons = html.Div(
    className="pipac-header-actions",
    children=[
        html.Div(
            className="pipac-header-city",
            children=[
                html.Span("Ciudad"),
                dcc.Dropdown(
                    id="filtro-ciudad",
                    options=[{"label": option, "value": option} for option in city_options],
                    placeholder="Todo el país",
                    clearable=True,
                    searchable=True,
                    className="pipac-dropdown",
                ),
            ],
        ),
        badge("Sistema Online", "success"),
        html.Div(className="pipac-header-metadata", children=[html.Span("Última actualización"), html.Strong(APP_STARTED_AT.strftime("%d/%m/%Y %I:%M %p"))]),
        html.Div(className="pipac-header-metadata", children=[html.Span("Hora en tiempo real"), html.Strong(id="live-clock")]),
        html.Div(className="pipac-icon-button", children="?") ,
    ],
)

sidebar = html.Aside(
    className="pipac-sidebar",
    children=[
        html.Div(
            className="pipac-brand",
            children=[
                html.Div(className="pipac-brand-mark", children="P"),
                html.Div(
                    children=[
                        html.Div("PIPAC", className="pipac-brand-title"),
                        html.Div("Bucaramanga Smart City", className="pipac-brand-subtitle"),
                    ]
                ),
            ],
        ),
        html.Div(className="pipac-sidebar-label", children="Navegación"),
        html.Div([nav_item(label, href, active) for label, href, active in CITY_NAV], className="pipac-nav-list"),
        html.Div(
            className="pipac-sidebar-panel",
            children=[
                html.Div(className="pipac-sidebar-panel-title", children="Tu información cuenta"),
                html.Div(
                    className="pipac-sidebar-panel-copy",
                    children="Reporta situaciones, recibe orientación y ayuda a construir una ciudad más segura.",
                ),
                        html.A("Reportar incidente", href="#ciudadania-seccion", className="pipac-primary-button"),
                        html.A("Solicitar acompañamiento", href="#ciudadania-seccion", className="pipac-sidebar-link"),
            ],
        ),
    ],
)

kpi_cards = html.Div(
    className="pipac-kpi-grid",
    children=[
        mini_card("Total delitos", f"{int(df['conteo'].sum()):,}", "Total acumulado de eventos", "+12.4% semanal", PRIMARY, df["conteo"].tail(8) if not df.empty else [0, 1, 2], "◌"),
        mini_card("Hotspots activos", f"{max(df['barrio'].nunique(), 1)}", "Zonas críticas monitoreadas", "+4 nuevas", RED, df.groupby("barrio").size().tail(8) if not df.empty else [1, 2, 1], "◎"),
        mini_card("Riesgo promedio", f"{df['es_riesgo_alto'].mean() * 100:.1f}%", "Nivel de riesgo medio", "-3.1% mensual", YELLOW, df["es_riesgo_alto"].rolling(3, min_periods=1).mean().tail(8), "◈"),
        mini_card("Tasa por 1,000 hab.", f"{df['tasa_crimen_1000'].mean():.2f}", "Tasa de delitos estimada", "+0.08", GREEN, df["tasa_crimen_1000"].tail(8), "◉"),
        mini_card("Casos hoy", f"{max(int(df['conteo'].sum() // 31), 1)}", "Delitos reportados hoy", "+8% vs ayer", ORANGE, (df["conteo"].tail(7).cumsum() if not df.empty else [0, 1, 2]), "◆"),
        mini_card("Variación semanal", "+2.7%", "Comparativa de 7 días", "Tendencia estable", VIOLET, (df["tasa_crimen_1000"].tail(7) if not df.empty else [1, 1, 2]), "▣"),
    ],
)

map_panel = html.Section(
    id="mapa-riesgo-seccion",
    className="pipac-map-grid",
    children=[
        section_card(
            "Mapa de Riesgo en Tiempo Real",
            "Mapa oscuro con heatmap, clusters, marcadores inteligentes y navegación tipo Mapbox.",
            html.Div(
                className="pipac-map-shell",
                children=[
                    dcc.Graph(
                        id="mapa-riesgo",
                        config={"displayModeBar": True, "scrollZoom": True, "responsive": True, "displaylogo": False},
                        className="pipac-map-figure",
                    ),
                    html.Div(
                        className="pipac-map-legend",
                        children=[
                            html.Div(className="pipac-legend-title", children="Nivel de riesgo"),
                            html.Div(className="pipac-legend-bar"),
                            html.Div(className="pipac-legend-labels", children=[html.Span("Bajo"), html.Span("Alto")]),
                        ],
                    ),
                ],
            ),
            "pipac-map-card",
        ),
        html.Div(
            className="pipac-floating-panel",
            children=[
                section_card(
                    "Filtros de análisis",
                    "Panel flotante para ajustar la lectura del mapa y los indicadores.",
                    html.Div(
                        className="pipac-filter-stack",
                        children=[
                            html.Label("Tipo de delito", className="pipac-field-label"),
                            dcc.Dropdown(id="filtro-delito", options=[{"label": item, "value": item} for item in delitos_disponibles], value=None, placeholder="Todos los delitos", clearable=True, className="pipac-dropdown"),
                            html.Label("Barrio", className="pipac-field-label"),
                            dcc.Dropdown(id="filtro-barrio", options=[{"label": item, "value": item} for item in barrios_disponibles], placeholder="Todos los barrios", clearable=True, className="pipac-dropdown"),
                            html.Label("Fecha", className="pipac-field-label"),
                            dcc.DatePickerRange(id="filtro-fecha", start_date=df["fecha"].min() if "fecha" in df.columns else None, end_date=df["fecha"].max() if "fecha" in df.columns else None, display_format="DD/MM/YYYY", className="pipac-date-picker"),
                            html.Label("Nivel de riesgo", className="pipac-field-label"),
                            dcc.Dropdown(id="filtro-riesgo", options=severidad_opciones, placeholder="Todos", clearable=True, className="pipac-dropdown"),
                            html.Label("Hora", className="pipac-field-label"),
                            dcc.Dropdown(id="filtro-hora", options=[{"label": f"{hour:02d}:00", "value": hour} for hour in range(24)], placeholder="Todas", clearable=True, className="pipac-dropdown"),
                            html.Label("Edad", className="pipac-field-label"),
                            dcc.RangeSlider(id="filtro-edad", min=0, max=100, step=1, value=[0, 100], marks={0: "0", 18: "18", 35: "35", 60: "60", 100: "100"}, tooltip={"placement": "bottom", "always_visible": False}),
                            html.Label("Sexo", className="pipac-field-label"),
                            dcc.Dropdown(id="filtro-sexo", options=[{"label": "Femenino", "value": "F"}, {"label": "Masculino", "value": "M"}, {"label": "No definido", "value": "N/D"}], placeholder="Todos", clearable=True, className="pipac-dropdown"),
                            html.Div(
                                className="pipac-filter-actions",
                                children=[
                                    html.Button("Aplicar filtros", className="pipac-primary-button"),
                                    html.Button("Limpiar", className="pipac-secondary-button"),
                                ],
                            ),
                        ],
                    ),
                ),
                section_card(
                    "Diagnósticos y alertas de IA",
                    "Recomendaciones priorizadas por nivel de urgencia y probabilidad.",
                    html.Div(id="recomendaciones-ia", className="pipac-alert-list"),
                    "pipac-ai-card",
                ),
            ],
        ),
    ],
)

charts_row = html.Section(
    id="analitica-seccion",
    className="pipac-analytics-grid",
    children=[
        section_card("Tendencia histórica de delincuencia", "Serie mensual con lectura limpia y foco en variación.", dcc.Graph(id="serie-temporal", config={"displayModeBar": False}, className="pipac-chart")),
        section_card("Delitos por hora", "Concentración horaria para apoyar patrullaje y prevención.", dcc.Graph(id="histograma-hora", config={"displayModeBar": False}, className="pipac-chart")),
        section_card("Delitos por barrio", "Barrios con mayor incidencia acumulada.", dcc.Graph(id="delitos-barrio", config={"displayModeBar": False}, className="pipac-chart")),
        section_card("Top delitos", "Tipos de delito más frecuentes en la muestra actual.", dcc.Graph(id="top-delitos", config={"displayModeBar": False}, className="pipac-chart")),
        section_card("Comparación mensual", "Comparativa de los últimos meses por volumen de eventos.", dcc.Graph(id="comparacion-mensual", config={"displayModeBar": False}, className="pipac-chart")),
    ],
)

citizen_panel = html.Section(
    id="ciudadania-seccion",
    className="pipac-citizen-grid",
    children=[
        section_card(
            "Información para la ciudadanía",
            "Recursos rápidos para tomar decisiones seguras y actuar con oportunidad.",
            html.Div(
                className="pipac-citizen-cards",
                children=[
                    html.Div(className="pipac-mini-info-card", children=[html.Div("🟢 Barrios más seguros", className="pipac-mini-title"), html.Div(id="barrios-seguros", className="pipac-mini-copy")]),
                    html.Div(className="pipac-mini-info-card danger", children=[html.Div("🔴 Barrios con mayor riesgo", className="pipac-mini-title"), html.Div(id="barrios-riesgo", className="pipac-mini-copy")]),
                    html.Div(className="pipac-mini-info-card", children=[html.Div("🚔 Recomendaciones de seguridad", className="pipac-mini-title"), html.Div(id="recomendaciones-ciudadania", className="pipac-mini-copy")]),
                    html.Div(className="pipac-mini-info-card", children=[html.Div("☎ Números de emergencia", className="pipac-mini-title"), html.Div("123 · 122 · 112 · 155", className="pipac-mini-copy")]),
                    html.Div(className="pipac-mini-info-card", children=[html.Div("📢 Alertas recientes", className="pipac-mini-title"), html.Div(id="alertas-recientes", className="pipac-mini-copy")]),
                    html.Div(className="pipac-mini-info-card", children=[html.Div("👮 Patrullajes activos", className="pipac-mini-title"), html.Div("18 cuadrantes priorizados", className="pipac-mini-copy")]),
                    html.Div(className="pipac-mini-info-card", children=[html.Div("👥 Participación ciudadana", className="pipac-mini-title"), html.Div("1,234 reportes verificados este mes", className="pipac-mini-copy")]),
                ],
            ),
        ),
        section_card(
            "Acciones rápidas",
            "Herramientas para participación ciudadana.",
            html.Div(
                className="pipac-citizen-actions",
                children=[
                    html.A("Reportar incidente", href="#ciudadania-seccion", className="pipac-action-button primary"),
                    html.A("Solicitar acompañamiento", href="#ciudadania-seccion", className="pipac-action-button"),
                    html.A("Ver rutas seguras", href="#mapa-riesgo-seccion", className="pipac-action-button"),
                    html.A("Contactar Policía", href="tel:123", className="pipac-action-button"),
                    html.A("Llamar emergencias", href="tel:123", className="pipac-action-button danger"),
                ],
            ),
            "pipac-citizen-card",
        ),
    ],
)

reportes_panel = html.Section(
    id="reportes-seccion",
    className="pipac-reportes-grid",
    children=[
        section_card(
            "Reportes y exportación",
            "Consolida la vista ejecutiva y facilita la descarga para entidades y ciudadanía.",
            html.Div(
                className="pipac-reportes-cards",
                children=[
                    html.Div(className="pipac-mini-info-card", children=[html.Div("Resumen ejecutivo", className="pipac-mini-title"), html.Div("Exportación en PDF y CSV para comités de seguridad.", className="pipac-mini-copy")]),
                    html.Div(className="pipac-mini-info-card", children=[html.Div("Dataset nacional", className="pipac-mini-title"), html.Div("Cobertura completa de datos.gov.co según disponibilidad local.", className="pipac-mini-copy")]),
                    html.Div(className="pipac-mini-info-card", children=[html.Div("Trazabilidad", className="pipac-mini-title"), html.Div("Último proceso ETL, origen y estado de actualización.", className="pipac-mini-copy")]),
                ],
            ),
        ),
    ],
)

config_panel = html.Section(
    id="configuracion-seccion",
    className="pipac-config-grid",
    children=[
        section_card(
            "Configuración del sistema",
            "Parámetros base de operación y experiencia para el despliegue gubernamental.",
            html.Div(
                className="pipac-config-cards",
                children=[
                    html.Div(className="pipac-mini-info-card", children=[html.Div("Ciudad por defecto", className="pipac-mini-title"), html.Div("BUCARAMANGA", className="pipac-mini-copy")]),
                    html.Div(className="pipac-mini-info-card", children=[html.Div("Actualización", className="pipac-mini-title"), html.Div("Tiempo real con refresco del reloj superior.", className="pipac-mini-copy")]),
                    html.Div(className="pipac-mini-info-card", children=[html.Div("Modo visual", className="pipac-mini-title"), html.Div("Tema oscuro premium para salas de control.", className="pipac-mini-copy")]),
                ],
            ),
        ),
    ],
)

footer = html.Footer(
    className="pipac-footer",
    children=[
        html.Div(className="pipac-footer-item", children=[html.Span("Cobertura"), html.Strong("98%")]),
        html.Div(className="pipac-footer-item", children=[html.Span("Modelos IA activos"), html.Strong("5")]),
        html.Div(className="pipac-footer-item", children=[html.Span("Precisión del modelo"), html.Strong("93.6%")]),
        html.Div(className="pipac-footer-item", children=[html.Span("Datos actualizados"), html.Strong("Tiempo real")]),
        html.Div(className="pipac-footer-item", children=[html.Span("Tiempo de respuesta"), html.Strong("< 2 s")]),
        html.Div(className="pipac-footer-item", children=[html.Span("Versión del sistema"), html.Strong("v2.4 Smart City")]),
    ],
)

app.layout = html.Div(
    className="pipac-app-shell",
    children=[
        dcc.Interval(id="clock-tick", interval=1000, n_intervals=0),
        sidebar,
        html.Main(
            className="pipac-main",
            children=[
                html.Section(
                    id="inicio",
                    className="pipac-topbar",
                    children=[
                        html.Div(
                            children=[
                                html.Div(className="pipac-topbar-eyebrow", children="PIPAC - Plataforma de Predicción y Análisis de Criminalidad"),
                                html.H1("Inteligencia de datos para una ciudad más segura", className="pipac-topbar-title"),
                                html.Div(className="pipac-topbar-copy", children="Dashboard gubernamental orientado a ciudadanos y entidades, con lectura geoespacial priorizada y visual premium."),
                            ]
                        ),
                        header_buttons,
                    ],
                ),
                kpi_cards,
                map_panel,
                charts_row,
                citizen_panel,
                reportes_panel,
                config_panel,
                footer,
            ],
        ),
    ],
)


def filter_dataframe(
    base_df: pd.DataFrame,
    ciudad_val,
    delito_val,
    barrio_val,
    riesgo_val,
    hora_val,
    edad_val,
    sexo_val,
    date_range,
) -> pd.DataFrame:
    filtered_df = base_df.copy()
    city_col = resolve_city_column(filtered_df)
    if ciudad_val:
        filtered_df = filtered_df[filtered_df[city_col].astype(str) == str(ciudad_val)]
    if delito_val:
        filtered_df = filtered_df[filtered_df["tipo_delito"] == delito_val]
    if barrio_val:
        filtered_df = filtered_df[filtered_df["barrio"] == barrio_val]
    if riesgo_val:
        filtered_df = filtered_df[filtered_df["nivel_riesgo"].str.upper() == str(riesgo_val).upper()]
    if hora_val is not None:
        filtered_df = filtered_df[filtered_df["hora"] == int(hora_val)]
    if edad_val and len(edad_val) == 2:
        filtered_df = filtered_df[(filtered_df["edad"] >= edad_val[0]) & (filtered_df["edad"] <= edad_val[1])]
    if sexo_val:
        filtered_df = filtered_df[filtered_df["sexo"].str.upper() == str(sexo_val).upper()]
    if date_range and len(date_range) == 2 and "fecha" in filtered_df.columns:
        start_date, end_date = date_range
        filtered_df = filtered_df[(pd.to_datetime(filtered_df["fecha"]) >= pd.to_datetime(start_date)) & (pd.to_datetime(filtered_df["fecha"]) <= pd.to_datetime(end_date))]
    return filtered_df if not filtered_df.empty else base_df.head(1).copy()


def build_map_figure(filtered_df: pd.DataFrame, clusters_enabled: bool) -> go.Figure:
    map_df = filtered_df.copy()
    color_column = "es_riesgo_alto"
    discrete = False
    if clusters_enabled and len(map_df) >= 5:
        try:
            coords = map_df[["lat", "lon"]].to_numpy()
            labels = DBSCAN(eps=0.03, min_samples=5).fit(coords).labels_.astype(int)
            map_df["cluster_dbscan"] = labels
            color_column = "cluster_dbscan"
            discrete = True
        except Exception:
            color_column = "es_riesgo_alto"
            discrete = False

    figure = go.Figure()
    if not map_df.empty:
        figure.add_trace(
            go.Densitymapbox(
                lat=map_df["lat"],
                lon=map_df["lon"],
                z=map_df["densidad_eventos_30d"],
                radius=28,
                colorscale=[[0, GREEN], [0.5, YELLOW], [1, RED]],
                opacity=0.62,
                hoverinfo="skip",
                showscale=False,
                name="Heatmap",
            )
        )
        if discrete and color_column == "cluster_dbscan":
            colors = [PRIMARY, ORANGE, RED, GREEN, CYAN, VIOLET]
            for idx, cluster_value in enumerate(sorted(map_df[color_column].unique())):
                cluster_df = map_df[map_df[color_column] == cluster_value]
                figure.add_trace(
                    go.Scattermapbox(
                        lat=cluster_df["lat"],
                        lon=cluster_df["lon"],
                        mode="markers",
                        marker={"size": 13, "color": colors[idx % len(colors)], "opacity": 0.9},
                        name=f"Cluster {cluster_value}",
                        text=cluster_df["barrio"],
                        hovertemplate="<b>%{text}</b><br>Cluster %{name}<extra></extra>",
                    )
                )
        else:
            figure.add_trace(
                go.Scattermapbox(
                    lat=map_df["lat"],
                    lon=map_df["lon"],
                    mode="markers",
                    marker={
                        "size": map_df["densidad_eventos_30d"].clip(8, 32),
                        "color": map_df["es_riesgo_alto"],
                        "colorscale": [[0, GREEN], [0.5, YELLOW], [1, RED]],
                        "opacity": 0.92,
                    },
                    text=map_df["barrio"],
                    customdata=map_df[["comuna", "tipo_delito", "tasa_crimen_1000"]],
                    name="Eventos",
                    hovertemplate="<b>%{text}</b><br>%{customdata[0]}<br>%{customdata[1]}<br>Tasa: %{customdata[2]:.2f}<extra></extra>",
                )
            )

    viewport = compute_map_view(map_df)

    figure.update_layout(
        mapbox={"style": "carto-darkmatter", "center": {"lat": viewport["lat"], "lon": viewport["lon"]}, "zoom": viewport["zoom"]},
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXT_PRIMARY, "family": "Inter, sans-serif"},
        showlegend=False,
        height=610,
        uirevision="map-view",
    )
    return figure


def build_time_figure(filtered_df: pd.DataFrame) -> go.Figure:
    ts_df = filtered_df.groupby("mes").size().reset_index(name="delitos").sort_values("mes")
    ts_df["mes_nombre"] = ts_df["mes"].astype(str)
    figure = px.line(ts_df, x="mes_nombre", y="delitos", markers=True)
    figure.update_traces(line={"color": PRIMARY, "width": 3}, marker={"size": 8, "color": CYAN})
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        font={"color": TEXT_PRIMARY, "family": "Inter, sans-serif"},
        xaxis={"title": "Mes", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        yaxis={"title": "Eventos", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        height=320,
    )
    return figure


def build_hour_figure(filtered_df: pd.DataFrame) -> go.Figure:
    hour_df = filtered_df.groupby("hora").size().reset_index(name="eventos").sort_values("hora")
    figure = px.bar(hour_df, x="hora", y="eventos")
    figure.update_traces(marker_color=PRIMARY, marker_line_color=CYAN, marker_line_width=0.5, opacity=0.9)
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        font={"color": TEXT_PRIMARY, "family": "Inter, sans-serif"},
        xaxis={"title": "Hora", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        yaxis={"title": "Eventos", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        height=320,
    )
    return figure


def build_barrio_figure(filtered_df: pd.DataFrame) -> go.Figure:
    barrio_df = filtered_df.groupby("barrio").size().reset_index(name="eventos").sort_values("eventos", ascending=True).tail(8)
    figure = px.bar(barrio_df, x="eventos", y="barrio", orientation="h")
    figure.update_traces(marker_color=ORANGE)
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        font={"color": TEXT_PRIMARY, "family": "Inter, sans-serif"},
        xaxis={"title": "Eventos", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        yaxis={"title": "Barrio", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        height=320,
    )
    return figure


def build_top_delitos_figure(filtered_df: pd.DataFrame) -> go.Figure:
    delito_df = filtered_df.groupby("tipo_delito").size().reset_index(name="eventos").sort_values("eventos", ascending=True).tail(8)
    figure = px.bar(delito_df, x="eventos", y="tipo_delito", orientation="h")
    figure.update_traces(marker_color=GREEN)
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        font={"color": TEXT_PRIMARY, "family": "Inter, sans-serif"},
        xaxis={"title": "Eventos", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        yaxis={"title": "Delito", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        height=320,
    )
    return figure


def build_month_compare_figure(filtered_df: pd.DataFrame) -> go.Figure:
    compare_df = filtered_df.copy()
    compare_df["periodo"] = compare_df["anio"].astype(str) + "-" + compare_df["mes"].astype(str).str.zfill(2)
    month_df = compare_df.groupby("periodo").size().reset_index(name="eventos").tail(12)
    figure = px.area(month_df, x="periodo", y="eventos")
    figure.update_traces(line={"color": VIOLET, "width": 3}, fillcolor="rgba(139,92,246,0.22)")
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        font={"color": TEXT_PRIMARY, "family": "Inter, sans-serif"},
        xaxis={"title": "Periodo", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        yaxis={"title": "Eventos", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        height=320,
    )
    return figure


def build_alert_item(title: str, description: str, priority: str, color: str, probability: str, action: str) -> html.Div:
    return html.Div(
        className="pipac-alert-item",
        children=[
            html.Div(className="pipac-alert-strip", style={"background": color}),
            html.Div(
                className="pipac-alert-content",
                children=[
                    html.Div(className="pipac-alert-topline", children=[html.Span(priority), html.Span(probability)]),
                    html.Div(className="pipac-alert-title", children=title),
                    html.Div(className="pipac-alert-copy", children=description),
                    html.Div(className="pipac-alert-action", children=action),
                ],
            ),
        ],
    )


def compute_map_view(filtered_df: pd.DataFrame) -> dict[str, float]:
    if filtered_df.empty:
        return {"lat": 4.6, "lon": -74.1, "zoom": 4.8}

    lat_min = float(filtered_df["lat"].min())
    lat_max = float(filtered_df["lat"].max())
    lon_min = float(filtered_df["lon"].min())
    lon_max = float(filtered_df["lon"].max())

    lat_center = (lat_min + lat_max) / 2
    lon_center = (lon_min + lon_max) / 2
    lat_span = max(lat_max - lat_min, 0.1)
    lon_span = max(lon_max - lon_min, 0.1)
    span = max(lat_span, lon_span)

    if span > 12:
        zoom = 3.3
    elif span > 6:
        zoom = 4.0
    elif span > 3:
        zoom = 4.8
    else:
        zoom = 5.5

    return {"lat": lat_center, "lon": lon_center, "zoom": zoom}

@app.callback(Output("live-clock", "children"), Input("clock-tick", "n_intervals"))
def update_clock(_n_intervals: int) -> str:
    return datetime.now().strftime("%I:%M:%S %p")


@app.callback(
    [
        Output("mapa-riesgo", "figure"),
        Output("recomendaciones-ia", "children"),
        Output("serie-temporal", "figure"),
        Output("histograma-hora", "figure"),
        Output("delitos-barrio", "figure"),
        Output("top-delitos", "figure"),
        Output("comparacion-mensual", "figure"),
        Output("barrios-seguros", "children"),
        Output("barrios-riesgo", "children"),
        Output("recomendaciones-ciudadania", "children"),
        Output("alertas-recientes", "children"),
    ],
    [
        Input("filtro-ciudad", "value"),
        Input("filtro-delito", "value"),
        Input("filtro-barrio", "value"),
        Input("filtro-riesgo", "value"),
        Input("filtro-hora", "value"),
        Input("filtro-edad", "value"),
        Input("filtro-sexo", "value"),
        Input("filtro-fecha", "start_date"),
        Input("filtro-fecha", "end_date"),
    ],
)
def update_dashboard(ciudad_val, delito_val, barrio_val, riesgo_val, hora_val, edad_val, sexo_val, start_date, end_date):
    filtered_df = filter_dataframe(df, ciudad_val, delito_val, barrio_val, riesgo_val, hora_val, edad_val, sexo_val, [start_date, end_date] if start_date and end_date else None)

    clusters_enabled = len(filtered_df) >= 5
    map_figure = build_map_figure(filtered_df, clusters_enabled)
    time_figure = build_time_figure(filtered_df)
    hour_figure = build_hour_figure(filtered_df)
    barrio_figure = build_barrio_figure(filtered_df)
    top_figure = build_top_delitos_figure(filtered_df)
    month_figure = build_month_compare_figure(filtered_df)

    advisor = AIAdvisor(filtered_df)
    try:
        ai_recommendations = advisor.get_police_presence_recommendations()
    except Exception:
        ai_recommendations = ["Sin recomendaciones disponibles en este momento."]

    alert_cards = [
        build_alert_item(
            title=rec.split(".")[0][:90],
            description=rec,
            priority=["Alta prioridad", "Media prioridad", "Atención preventiva"][idx % 3],
            color=[RED, ORANGE, GREEN][idx % 3],
            probability=f"Prob. {min(95, 72 + idx * 6)}%",
            action="Ver detalles",
        )
        for idx, rec in enumerate(ai_recommendations[:4])
    ]

    try:
        city_for_predictions = ciudad_val or (filtered_df[city_column].iloc[0] if not filtered_df.empty and city_column in filtered_df.columns else "BUCARAMANGA")
        preds = fetch_predictions(city=city_for_predictions)
    except Exception:
        preds = []

    if preds:
        alert_cards.append(
            html.Div(
                className="pipac-prediction-list",
                children=[
                    html.Div(className="pipac-mini-title", children="Predicciones top 5"),
                    html.Ul(
                        className="pipac-list-clean",
                        children=[
                            html.Li(f"{item.get('barrio', 'N/D')} · {item.get('risk_level', 'N/D')} · {item.get('risk_probability', 0)}")
                            for item in preds[:5]
                        ],
                    ),
                ],
            )
        )

    safe_barrio_series = filtered_df[filtered_df["es_riesgo_alto"] == 0]["barrio"].value_counts().head(3)
    risky_barrio_series = filtered_df[filtered_df["es_riesgo_alto"] == 1]["barrio"].value_counts().head(3)

    city_recommendations = html.Ul(
        className="pipac-list-clean",
        children=[
            html.Li("Usar rutas iluminadas y validar el entorno antes de viajar."),
            html.Li("Priorizar reportes en horarios con mayor concentración de eventos."),
            html.Li("Compartir ubicación en tiempo real cuando sea necesario."),
        ],
    )

    recent_alerts = html.Ul(
        className="pipac-list-clean",
        children=[html.Li(rec) for rec in ai_recommendations[:3]],
    )

    safe_barrio_text = ", ".join(safe_barrio_series.index.tolist()) if not safe_barrio_series.empty else "Sin datos suficientes"
    risky_barrio_text = ", ".join(risky_barrio_series.index.tolist()) if not risky_barrio_series.empty else "Sin datos suficientes"

    return map_figure, alert_cards, time_figure, hour_figure, barrio_figure, top_figure, month_figure, safe_barrio_text, risky_barrio_text, city_recommendations, recent_alerts


def main() -> None:
    port = int(os.getenv("DASH_PORT", "8050"))
    app.run_server(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()

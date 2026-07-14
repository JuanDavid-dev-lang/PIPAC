# Arquitectura

## Capas

- Ingesta: Socrata API de datos.gov.co.
- ETL: limpieza, homologacion, normalizacion y control de calidad.
- Almacenamiento: PostgreSQL con PostGIS.
- Features: ventanas temporales, tasas, densidades y variables geograficas.
- ML: comparacion de Logistic Regression, Random Forest, Gradient Boosting y XGBoost.
- Serving: FastAPI.
- Visualization: Plotly Dash, Folium y OpenStreetMap.
- Deployment: Docker y versionamiento con Git/GitHub.

## Flujo

1. Descarga del dataset.
2. Almacenamiento raw.
3. Limpieza y transformacion.
4. Carga a base geopacial.
5. Generacion de variables.
6. Entrenamiento y validacion.
7. Publicacion via API.
8. Consumo en dashboard y mapas.

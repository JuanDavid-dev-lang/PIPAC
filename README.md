# Plataforma Inteligente para la Prediccion y Analisis de Criminalidad mediante Inteligencia Artificial y Datos Abiertos

Proyecto base en Python 3.12 para analitica predictiva de criminalidad con datos abiertos de Colombia.

## Objetivo

Construir una plataforma que integre:

- recoleccion automatica de datos.gov.co
- ETL y homologacion territorial
- ingenieria de caracteristicas
- modelos de ML
- API REST
- dashboard con mapas y KPI

## Estructura

```text
Proyecto/
├── datasets/
├── models/
├── notebooks/
├── preprocessing/
├── api/
├── dashboard/
├── maps/
├── training/
├── utils/
├── config/
├── tests/
├── documentation/
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Datasets oficiales seleccionados

- [Informacion delictiva del municipio de Bucaramanga](https://www.datos.gov.co/Seguridad-y-Defensa/Informaci-n-delictiva-del-municipio-de-Bucaramanga/x46e-abhz)
- [Reporte Hurto por Modalidades Policia Nacional](https://www.datos.gov.co/Seguridad-y-Defensa/Reporte-Hurto-por-Modalidades-Polic-a-Nacional/d4fr-sbn2)
- [Accidentes de Transito ocurridos en el Municipio de Bucaramanga](https://www.datos.gov.co/Transporte/3-Accidentes-de-Transito-ocurridos-en-el-Municipio/7cci-nqqb)
- [Datos de proyeccion de poblacion de Bucaramanga desagregados por barrios y comunas](https://www.datos.gov.co/Vivienda-Ciudad-y-Territorio/Datos-de-proyecci-n-de-poblaci-n-de-Bucaramanga-de/kn95-8dei)
- [Gran Encuesta Integrada de Hogares - GEIH - 2026](https://www.datos.gov.co/dataset/Gran-Encuesta-Integrada-de-Hogares-GEIH-2026/nzxb-qax7)
- [Cartografia Urbana Catastral en formato geoDataBase Municipio de Bucaramanga](https://www.datos.gov.co/Vivienda-Ciudad-y-Territorio/23-Cartograf-a-Urbana-Catastral-en-formato-geoData/f4hz-53x5)
- [Trafico Vehicular ANI](https://www.datos.gov.co/Transporte/Tr-fico-Vehicular-ANI/8yi9-t44c)

## Ejecucion local

1. Crear entorno virtual e instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno:

```bash
copy .env.example .env
```

3. Levantar la API:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

4. Levantar el dashboard:

```bash
python -m dashboard.app
```

Por defecto el dashboard queda en `http://127.0.0.1:8050/`. Si necesitas otro puerto, define `DASHBOARD_PORT` antes de arrancarlo.

5. Generar mapa folium:

```bash
python -m maps.generate_maps
```

## Endpoints

- `GET /health`
- `GET /api/v1/crimes`
- `GET /api/v1/predictions`
- `GET /api/v1/stats`
- `GET /api/v1/alerts`
- `POST /api/v1/datasets/refresh`
- `POST /api/v1/train`
- `GET /api/v1/export/{format}`

## Observaciones

- El proyecto esta preparado para conectar la API Socrata de datos.gov.co.
- El dashboard inicial usa datos de demostracion hasta que el ETL cargue los datasets oficiales.
- La base espacial usa PostgreSQL + PostGIS.

## Migraciones PostGIS

Si tiene PostgreSQL con PostGIS, aplique el schema con el script incluido:

```bash
pip install psycopg2-binary
python scripts/migrate_postgis.py
```

## Ejecutar ETL (descarga desde datos.gov.co)

La API expone un endpoint para refrescar datasets localmente. Levante la API y ejecute:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/datasets/refresh/local
```

Esto descargará y procesará los datasets definidos en `config/settings.py` y guardará los parquet en `datasets/processed`.

## Notas sobre el dashboard

- El dashboard intenta cargar primero `datasets/processed/crime_hurtos_nacional.parquet`.
- Si no existe, intenta leer `crime_bga.parquet` o usa una versión simulada.
- También puede consumir la API local (`/api/v1/crimes`) para datos dinámicos.



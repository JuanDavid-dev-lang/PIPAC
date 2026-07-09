<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=30&pause=1000&color=00D4FF&center=true&vCenter=true&width=900&lines=🛡️+PIPAC+Platform;Predicción+Inteligente+de+Criminalidad;Inteligencia+Artificial+%2B+Datos+Abiertos;Colombia+🇨🇴" alt="Typing SVG" />

<br/>

<img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/Plotly_Dash-017CEE?style=for-the-badge&logo=plotly&logoColor=white"/>
<img src="https://img.shields.io/badge/PostgreSQL-PostGIS-336791?style=for-the-badge&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
<img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white"/>

<br/><br/>

<img src="https://img.shields.io/badge/Estado-En_Desarrollo-yellow?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Licencia-MIT-green?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Colombia-Escala_Nacional-FCD116?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5MDAgNjAwIj48cmVjdCB3aWR0aD0iOTAwIiBoZWlnaHQ9IjYwMCIgZmlsbD0iI0ZDRDExNiIvPjxyZWN0IHk9IjMwMCIgd2lkdGg9IjkwMCIgaGVpZ2h0PSIxNTAiIGZpbGw9IiMwMDM4OTMiLz48cmVjdCB5PSI0NTAiIHdpZHRoPSI5MDAiIGhlaWdodD0iMTUwIiBmaWxsPSIjQ0UxMTI2Ii8+PC9zdmc+"/>

<br/><br/>

> **Plataforma Nacional Inteligente para la Predicción y Análisis de Criminalidad**  
> *mediante Inteligencia Artificial y Datos Abiertos de Colombia*

---

</div>

## 📌 Tabla de Contenidos

- [🎯 Objetivo](#-objetivo)
- [⚡ Características Principales](#-características-principales)
- [🏗️ Arquitectura](#️-arquitectura)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [🗃️ Datasets Oficiales](#️-datasets-oficiales)
- [🚀 Instalación y Ejecución](#-instalación-y-ejecución)
- [🔌 API Endpoints](#-api-endpoints)
- [🗺️ Visualizaciones y Mapas](#️-visualizaciones-y-mapas)
- [🐳 Docker](#-docker)
- [🧪 Tests](#-tests)
- [📊 Tecnologías](#-tecnologías)

---

## 🎯 Objetivo

<div align="center">

```
╔══════════════════════════════════════════════════════════════════╗
║          🇨🇴  PIPAC  —  Colombia Segura con IA  🇨🇴              ║
║                                                                  ║
║   Integrar datos abiertos + Machine Learning para predecir,      ║
║   analizar y visualizar patrones de criminalidad en tiempo       ║
║   real a escala nacional.                                        ║
╚══════════════════════════════════════════════════════════════════╝
```

</div>

Construir una plataforma de **escala nacional** para Colombia que integre de forma unificada:

| 🔄 Módulo | 📋 Descripción |
|---|---|
| 📥 **Ingesta de Datos** | Recolección automática desde datos.gov.co vía API Socrata |
| 🔧 **ETL & Homologación** | Limpieza, normalización y homologación territorial municipal |
| 🧠 **Feature Engineering** | Ingeniería de características criminológicas avanzadas |
| 🤖 **Modelos de ML** | Predicción con Random Forest, XGBoost, LSTM y más |
| ⚡ **API REST** | FastAPI con documentación automática Swagger/OpenAPI |
| 🗺️ **Dashboard Interactivo** | Mapas Folium + KPIs en tiempo real con Plotly Dash |
| 🗄️ **Base Espacial** | PostgreSQL + PostGIS para datos geoespaciales |

---

## ⚡ Características Principales

<div align="center">

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   🔴 TIEMPO REAL    🟡 PREDICCIÓN    🟢 VISUALIZACIÓN           │
│                                                                 │
│   ✅ Datos oficiales datos.gov.co      ✅ API REST moderna       │
│   ✅ ETL automatizado y escalable      ✅ Mapas geoespaciales    │
│   ✅ Modelos ML entrenados             ✅ Dashboard interactivo  │
│   ✅ Alertas tempranas                 ✅ Exportación múltiple   │
│   ✅ Cobertura nacional Colombia       ✅ Dockerizado            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

</div>

---

## 🏗️ Arquitectura

```
                        ┌─────────────────────┐
                        │   datos.gov.co 🌐   │
                        │   API Socrata        │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │   ETL & Preproceso  │
                        │   preprocessing/    │
                        └──────────┬──────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
           ┌──────────────┐ ┌──────────┐ ┌──────────────┐
           │  PostgreSQL  │ │ Parquet  │ │  GeoJSON /   │
           │  + PostGIS 🗄│ │ datasets │ │  Shapefiles  │
           └──────┬───────┘ └────┬─────┘ └──────┬───────┘
                  └──────────────┼───────────────┘
                                 │
                                 ▼
                        ┌─────────────────────┐
                        │   Modelos de ML 🤖  │
                        │   training/         │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │   FastAPI REST ⚡   │
                        │   api/              │
                        └──────────┬──────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼                             ▼
           ┌──────────────┐             ┌──────────────┐
           │ Dashboard 📊 │             │  Mapas 🗺️   │
           │ Plotly Dash  │             │  Folium      │
           └──────────────┘             └──────────────┘
```

---

## 📁 Estructura del Proyecto

```
📦 PIPAC/
├── 📂 api/                     ← FastAPI: endpoints REST
│   ├── main.py
│   ├── routes/
│   └── schemas/
├── 📂 dashboard/               ← Plotly Dash: visualización interactiva
│   └── app.py
├── 📂 preprocessing/           ← ETL: limpieza y transformación
├── 📂 training/                ← Entrenamiento de modelos ML
├── 📂 models/                  ← Modelos serializados (.pkl, .joblib)
├── 📂 datasets/                ← Datos crudos y procesados
│   ├── raw/
│   └── processed/
├── 📂 maps/                    ← Mapas Folium y GeoJSON
├── 📂 notebooks/               ← Análisis exploratorio Jupyter
├── 📂 config/                  ← Configuración y settings
├── 📂 utils/                   ← Utilidades compartidas
├── 📂 scripts/                 ← Scripts de migración y admin
├── 📂 tests/                   ← Suite de pruebas
├── 📂 documentation/           ← Documentación técnica
├── 🐳 Dockerfile.api
├── 🐳 Dockerfile.dashboard
├── 🐳 docker-compose.yml
├── ⚙️  .env.example
├── 📋 requirements.txt
└── 📖 README.md
```

---

## 🗃️ Datasets Oficiales

> 📡 Todos los datos provienen del portal oficial **[datos.gov.co](https://www.datos.gov.co/)** de Colombia

| # | 📊 Dataset | 🏷️ Categoría | 🔗 Enlace |
|---|---|---|---|
| 1 | 📌 Información Delictiva Municipal Histórica | Seguridad | [Ver dataset](https://www.datos.gov.co/Seguridad-y-Defensa/Informaci-n-delictiva-del-municipio-de-Bucaramanga/x46e-abhz) |
| 2 | 🔍 Reporte Hurto por Modalidades - Policía Nacional | Seguridad | [Ver dataset](https://www.datos.gov.co/Seguridad-y-Defensa/Reporte-Hurto-por-Modalidades-Polic-a-Nacional/d4fr-sbn2) |
| 3 | 🚗 Accidentes de Tránsito Municipales | Transporte | [Ver dataset](https://www.datos.gov.co/Transporte/3-Accidentes-de-Transito-ocurridos-en-el-Municipio/7cci-nqqb) |
| 4 | 👥 Proyección Población Municipal (Barrios y Comunas) | Territorio | [Ver dataset](https://www.datos.gov.co/Vivienda-Ciudad-y-Territorio/Datos-de-proyecci-n-de-poblaci-n-de-Bucaramanga-de/kn95-8dei) |
| 5 | 📋 Gran Encuesta Integrada de Hogares - GEIH 2026 | Socioeconómico | [Ver dataset](https://www.datos.gov.co/dataset/Gran-Encuesta-Integrada-de-Hogares-GEIH-2026/nzxb-qax7) |
| 6 | 🗺️ Cartografía Urbana Catastral - Bucaramanga | GeoEspacial | [Ver dataset](https://www.datos.gov.co/Vivienda-Ciudad-y-Territorio/23-Cartograf-a-Urbana-Catastral-en-formato-geoData/f4hz-53x5) |
| 7 | 🛣️ Tráfico Vehicular ANI | Transporte | [Ver dataset](https://www.datos.gov.co/Transporte/Tr-fico-Vehicular-ANI/8yi9-t44c) |

---

## 🚀 Instalación y Ejecución

### Prerequisitos

```
✅ Python 3.12+
✅ PostgreSQL 14+ con PostGIS (opcional pero recomendado)
✅ Docker & Docker Compose (para ejecución contenida)
```

### ⚡ Inicio Rápido (Windows)

```batch
:: Doble clic en el archivo o ejecutar en terminal:
iniciar.bat
```

### 🐍 Instalación Manual

**Paso 1 — Clonar el repositorio**
```bash
git clone https://github.com/JuanDavid-dev-lang/PIPAC.git
cd PIPAC
```

**Paso 2 — Crear entorno virtual e instalar dependencias**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

**Paso 3 — Configurar variables de entorno**
```bash
copy .env.example .env   # Windows
cp .env.example .env     # Linux/macOS
# ✏️ Edita .env con tus credenciales
```

**Paso 4 — Levantar la API**
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
# 🌐 Disponible en: http://127.0.0.1:8000
# 📖 Swagger UI:    http://127.0.0.1:8000/docs
```

**Paso 5 — Levantar el Dashboard**
```bash
python -m dashboard.app
# 📊 Disponible en: http://127.0.0.1:8050
```

**Paso 6 — Generar mapas Folium**
```bash
python -m maps.generate_maps
# 🗺️ Mapas generados en: maps/output/
```

---

## 🔌 API Endpoints

<div align="center">

| Método | Endpoint | 📋 Descripción |
|---|---|---|
| `GET` | `/health` | ✅ Estado del sistema |
| `GET` | `/api/v1/crimes` | 🔴 Datos de criminalidad |
| `GET` | `/api/v1/predictions` | 🤖 Predicciones de ML |
| `GET` | `/api/v1/stats` | 📊 Estadísticas agregadas |
| `GET` | `/api/v1/alerts` | 🚨 Alertas activas |
| `POST` | `/api/v1/datasets/refresh` | 🔄 Refrescar datasets |
| `POST` | `/api/v1/train` | 🧠 Entrenar modelos |
| `GET` | `/api/v1/export/{format}` | 📤 Exportar datos (csv/json/xlsx) |

</div>

> 📖 Documentación interactiva completa disponible en **`/docs`** (Swagger UI) y **`/redoc`**

---

## 🗺️ Visualizaciones y Mapas

El sistema genera mapas interactivos con:

- 🔴 **Heatmaps de criminalidad** por municipio y departamento
- 📍 **Puntos de incidentes** geolocalizados
- 🔵 **Zonas de alto riesgo** predichas por ML
- 📈 **KPIs en tiempo real**: tasa delictiva, variación mensual, hotspots
- 🗺️ Capas GeoJSON con división político-administrativa de Colombia

---

## 🐳 Docker

```bash
# Levantar todos los servicios
docker-compose up --build

# Solo la API
docker-compose up api

# Solo el dashboard
docker-compose up dashboard
```

| Servicio | Puerto | URL |
|---|---|---|
| 🔌 API FastAPI | `8000` | http://localhost:8000/docs |
| 📊 Dashboard | `8050` | http://localhost:8050 |
| 🗄️ PostgreSQL | `5432` | localhost:5432 |

---

## 🗄️ Migraciones PostGIS

```bash
# Instalar driver PostgreSQL
pip install psycopg2-binary

# Aplicar schema espacial
python scripts/migrate_postgis.py
```

---

## 📥 Ejecutar ETL

```bash
# Descargar y procesar datasets desde datos.gov.co
curl -X POST http://127.0.0.1:8000/api/v1/datasets/refresh/local
```

> ⚙️ Los datasets se guardan en `datasets/processed/` como archivos `.parquet`

---

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con reporte de cobertura
pytest tests/ --cov=api --cov-report=html
```

---

## 📊 Tecnologías

<div align="center">

| Capa | Tecnología |
|---|---|
| 🐍 Lenguaje | Python 3.12 |
| ⚡ API | FastAPI + Uvicorn |
| 📊 Dashboard | Plotly Dash |
| 🤖 ML | scikit-learn, XGBoost, statsmodels |
| 🗺️ Mapas | Folium, GeoPandas |
| 🗄️ Base de Datos | PostgreSQL + PostGIS |
| 📦 Datos | Pandas, Polars, PyArrow (Parquet) |
| 🐳 Contenedores | Docker + Docker Compose |
| 🔗 Datos Abiertos | Socrata API (datos.gov.co) |

</div>

---

## 📝 Notas del Dashboard

```
📌 Orden de carga de datos:
   1️⃣  datasets/processed/crime_hurtos_nacional_featured.parquet
   2️⃣  datasets/processed/crime_hurtos_nacional.parquet
   3️⃣  datasets/processed/crime_bga.parquet
   4️⃣  API local → /api/v1/crimes
   5️⃣  Datos de demostración simulados (fallback)
```

---

<div align="center">

---

### 🇨🇴 Hecho con ❤️ para Colombia

*Contribuyendo a la seguridad ciudadana mediante tecnología e inteligencia artificial*

<br/>

<img src="https://img.shields.io/badge/Made_with-Python_🐍-3776AB?style=for-the-badge"/>
<img src="https://img.shields.io/badge/For-Colombia_🇨🇴-FCD116?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Powered_by-Open_Data-00D4FF?style=for-the-badge"/>

<br/><br/>

⭐ **¡Dale una estrella si este proyecto te parece útil!** ⭐

</div>

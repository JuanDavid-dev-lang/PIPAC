from dataclasses import dataclass
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://crime:crime@localhost:5432/crime_ai")
    socrata_app_token: str | None = os.getenv("SOCRATA_APP_TOKEN") or None
    socrata_base_url: str = os.getenv("SOCRATA_BASE_URL", "https://www.datos.gov.co/resource")
    default_city: str = os.getenv("DEFAULT_CITY", "BUCARAMANGA")
    timezone: str = os.getenv("TIMEZONE", "America/Bogota")


settings = Settings()


DATASETS = {
    "crime_bga": {
        "id": "x46e-abhz",
        "name": "Informacion delictiva del municipio de Bucaramanga",
        "source": "https://www.datos.gov.co/Seguridad-y-Defensa/Informaci-n-delictiva-del-municipio-de-Bucaramanga/x46e-abhz",
        "refresh": "quarterly",
    },
    "crime_hurtos_nacional": {
        "id": "d4fr-sbn2",
        "name": "Reporte Hurto por Modalidades Policia Nacional",
        "source": "https://www.datos.gov.co/Seguridad-y-Defensa/Reporte-Hurto-por-Modalidades-Polic-a-Nacional/d4fr-sbn2",
        "refresh": "quarterly",
    },
    "poblacion_bga": {
        "id": "kn95-8dei",
        "name": "Datos de proyeccion de poblacion de Bucaramanga desagregados por barrios y comunas",
        "source": "https://www.datos.gov.co/Vivienda-Ciudad-y-Territorio/Datos-de-proyecci-n-de-poblaci-n-de-Bucaramanga-de/kn95-8dei",
        "refresh": "annual",
    },
    "accidentes_bga": {
        "id": "7cci-nqqb",
        "name": "Accidentes de Transito ocurridos en el Municipio de Bucaramanga",
        "source": "https://www.datos.gov.co/Transporte/3-Accidentes-de-Transito-ocurridos-en-el-Municipio/7cci-nqqb",
        "refresh": "annual",
    },
    "geih": {
        "id": "nzxb-qax7",
        "name": "Gran Encuesta Integrada de Hogares GEIH 2026",
        "source": "https://www.datos.gov.co/dataset/Gran-Encuesta-Integrada-de-Hogares-GEIH-2026/nzxb-qax7",
        "refresh": "annual",
    },
}


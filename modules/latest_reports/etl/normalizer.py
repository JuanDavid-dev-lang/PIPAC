import json
import logging
from typing import Tuple, Optional
import pandas as pd

logger = logging.getLogger(__name__)

# Basic Divipola mockup for illustration. In production this would be loaded from a dataset or larger static dict
DIVIPOLA_DEPARTMENTS = {
    'ANTIOQUIA': '05',
    'ATLANTICO': '08',
    'BOGOTA D.C.': '11',
    'BOGOTA': '11',
    'BOLIVAR': '13',
    'BOYACA': '15',
    'CALDAS': '17',
    'CAQUETA': '18',
    'CAUCA': '19',
    'CESAR': '20',
    'CORDOBA': '23',
    'CUNDINAMARCA': '25',
    'CHOCO': '27',
    'HUILA': '41',
    'LA GUAJIRA': '44',
    'MAGDALENA': '47',
    'META': '50',
    'NARIÑO': '52',
    'NORTE DE SANTANDER': '54',
    'QUINDIO': '63',
    'RISARALDA': '66',
    'SANTANDER': '68',
    'SUCRE': '70',
    'TOLIMA': '73',
    'VALLE DEL CAUCA': '76',
    'VALLE': '76',
    'ARAUCA': '81',
    'CASANARE': '85',
    'PUTUMAYO': '86',
    'ARCHIPIELAGO DE SAN ANDRES': '88',
    'AMAZONAS': '91',
    'GUAINIA': '94',
    'GUAVIARE': '95',
    'VAUPES': '97',
    'VICHADA': '99'
}

CITY_CENTROIDS = {
    'BOGOTÁ, D.C.': (4.6097, -74.0817),
    'MEDELLIN': (6.2442, -75.5812),
    'CALI': (3.4516, -76.5320),
    'BARRANQUILLA': (10.9685, -74.7813),
    'CARTAGENA': (10.3910, -75.4794),
    'CUCUTA': (7.8939, -72.5078),
    'BUCARAMANGA': (7.1193, -73.1227),
    'PEREIRA': (4.8133, -75.6961),
    'SANTA MARTA': (11.2408, -74.1990),
    'IBAGUE': (4.4389, -75.2322),
    'PASTO': (1.2136, -77.2811),
    'MANIZALES': (5.0703, -75.5138),
    'NEIVA': (2.9273, -75.2819),
    'VILLAVICENCIO': (4.1420, -73.6266),
    'ARMENIA': (4.5339, -75.6811),
    'VALLEDUPAR': (10.4742, -73.2436),
    'MONTERIA': (8.7480, -75.8814),
    'SINCELEJO': (9.3047, -75.3978),
    'POPAYAN': (2.4382, -76.6132),
    'TUNJA': (5.5353, -73.3678)
}


class TerritorialNormalizer:
    def normalize_departamento(self, name: str) -> Tuple[str, str]:
        if not name or pd.isna(name):
            return 'DESCONOCIDO', '00'
        
        name_clean = str(name).upper().strip()
        # Basic replacement
        if name_clean in DIVIPOLA_DEPARTMENTS:
            return name_clean, DIVIPOLA_DEPARTMENTS[name_clean]
        
        for k, v in DIVIPOLA_DEPARTMENTS.items():
            if k in name_clean:
                return k, v
                
        return name_clean, '00'

    def normalize_municipio(self, name: str, dept: Optional[str] = None) -> Tuple[str, str]:
        if not name or pd.isna(name):
            return 'DESCONOCIDO', '00000'
        
        name_clean = str(name).upper().strip()
        
        if name_clean == 'BOGOTA D.C.' or name_clean == 'BOGOTÁ, D.C.' or name_clean == 'BOGOTA':
            return 'BOGOTÁ, D.C.', '11001'
        
        return name_clean, '00000' # Placeholder for full DB lookup
        
    def get_centroid(self, municipio_name: str) -> Tuple[float, float]:
        name_clean = str(municipio_name).upper().strip()
        # Remove accents
        import unicodedata
        name_clean = ''.join(c for c in unicodedata.normalize('NFD', name_clean) if unicodedata.category(c) != 'Mn')
        
        if name_clean in CITY_CENTROIDS:
            return CITY_CENTROIDS[name_clean]
        
        # Default to approx center of Colombia if not found
        return (4.5709, -74.2973)

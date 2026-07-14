# Guia de Validacion

Esta guia permite revisar resultados de manera reproducible.

1. Instalar dependencias con `pip install -r requirements.txt`.
2. Ejecutar el ETL local con `python -m preprocessing.etl` o el endpoint de refresco de datos.
3. Entrenar modelos con `python -m training.train`.
4. Ejecutar pruebas con `python -m pytest`.
5. Revisar metricas en `models/*.metrics.json`.
6. Validar que las visualizaciones del dashboard y el frontend no presenten datos vacios inesperados.

## Criterios minimos

- Las columnas obligatorias del consolidado no deben quedar completamente nulas.
- Las coordenadas deben estar dentro de rangos validos.
- La inferencia del modelo debe devolver probabilidades entre 0 y 1.
- Las rutas principales de la API deben responder con estado 200.

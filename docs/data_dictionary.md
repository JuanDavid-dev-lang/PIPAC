# Diccionario de Datos

Variables principales del consolidado usado por PIPAC.

| Variable | Tipo | Descripcion |
|---|---|---|
| `fecha_hora` | datetime | Fecha y hora del hecho reportado. |
| `anio` | integer | Anio extraido de la fecha del hecho. |
| `mes` | integer | Mes del hecho reportado. |
| `dia` | integer | Dia del mes. |
| `dia_semana` | integer | Dia de la semana, con lunes como 0. |
| `hora` | integer | Hora del hecho. |
| `tipo_delito` | text | Categoria o modalidad del delito. |
| `departamento` | text | Departamento del registro. |
| `municipio` | text | Municipio del registro. |
| `barrio` | text | Barrio o unidad territorial disponible. |
| `comuna` | text | Comuna o agrupacion territorial. |
| `conteo` | integer | Cantidad de eventos representados por el registro. |
| `poblacion_total` | numeric | Poblacion estimada del territorio. |
| `tasa_crimen_1000` | numeric | Tasa de crimen por cada 1.000 habitantes. |
| `densidad_eventos_30d` | numeric | Suma movil de eventos en ventana de 30 dias. |
| `movilidad_intensidad` | numeric | Proxy territorial de movilidad. |
| `lat` | numeric | Latitud usada para visualizacion o agrupamiento. |
| `lon` | numeric | Longitud usada para visualizacion o agrupamiento. |
| `cluster_dbscan` | integer | Cluster espacial generado por DBSCAN. |
| `es_riesgo_alto` | integer | Variable objetivo binaria para riesgo alto. |

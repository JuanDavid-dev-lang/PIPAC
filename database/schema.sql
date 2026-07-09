CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS dim_territorio (
    territorio_id BIGSERIAL PRIMARY KEY,
    ciudad TEXT NOT NULL,
    departamento TEXT NOT NULL,
    barrio TEXT,
    comuna TEXT,
    zona_tipo TEXT,
    geom GEOMETRY(MULTIPOLYGON, 4326)
);

CREATE TABLE IF NOT EXISTS dim_tiempo (
    tiempo_id BIGSERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL,
    hora INTEGER,
    semana_anio INTEGER
);

CREATE TABLE IF NOT EXISTS fact_delitos (
    delito_id BIGSERIAL PRIMARY KEY,
    territorio_id BIGINT REFERENCES dim_territorio(territorio_id),
    tiempo_id BIGINT REFERENCES dim_tiempo(tiempo_id),
    tipo_delito TEXT NOT NULL,
    modalidad TEXT,
    conducta TEXT,
    arma TEXT,
    medio TEXT,
    conteo INTEGER DEFAULT 1,
    fuente TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fact_movilidad (
    movilidad_id BIGSERIAL PRIMARY KEY,
    territorio_id BIGINT REFERENCES dim_territorio(territorio_id),
    tiempo_id BIGINT REFERENCES dim_tiempo(tiempo_id),
    indicador TEXT NOT NULL,
    valor NUMERIC,
    fuente TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_sociodemografia (
    demo_id BIGSERIAL PRIMARY KEY,
    territorio_id BIGINT REFERENCES dim_territorio(territorio_id),
    tiempo_id BIGINT REFERENCES dim_tiempo(tiempo_id),
    indicador TEXT NOT NULL,
    valor NUMERIC,
    fuente TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS features_territoriales (
    feature_id BIGSERIAL PRIMARY KEY,
    territorio_id BIGINT REFERENCES dim_territorio(territorio_id),
    tiempo_id BIGINT REFERENCES dim_tiempo(tiempo_id),
    tasa_crimen_1000 NUMERIC,
    densidad_eventos_30d NUMERIC,
    poblacion_total NUMERIC,
    movilidad_intensidad NUMERIC,
    risk_score NUMERIC,
    feature_version TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS predicciones_riesgo (
    prediction_id BIGSERIAL PRIMARY KEY,
    territorio_id BIGINT REFERENCES dim_territorio(territorio_id),
    tiempo_id BIGINT REFERENCES dim_tiempo(tiempo_id),
    target_date DATE NOT NULL,
    risk_probability NUMERIC NOT NULL,
    risk_level TEXT NOT NULL,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alertas (
    alerta_id BIGSERIAL PRIMARY KEY,
    territorio_id BIGINT REFERENCES dim_territorio(territorio_id),
    tiempo_id BIGINT REFERENCES dim_tiempo(tiempo_id),
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dim_territorio_geom ON dim_territorio USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_fact_delitos_tipo_fecha ON fact_delitos (tipo_delito, tiempo_id);
CREATE INDEX IF NOT EXISTS idx_fact_delitos_fuente ON fact_delitos (fuente);
CREATE INDEX IF NOT EXISTS idx_predicciones_target_date ON predicciones_riesgo (target_date);

-- TABLAS DEL SISTEMA NACIONAL PIPAC V2
CREATE TABLE IF NOT EXISTS departamentos (
    id_departamento VARCHAR(2) PRIMARY KEY, -- Codigo DANE
    nombre TEXT NOT NULL,
    geom GEOMETRY(MULTIPOLYGON, 4326)
);

CREATE TABLE IF NOT EXISTS municipios (
    id_municipio VARCHAR(5) PRIMARY KEY, -- Codigo DANE
    id_departamento VARCHAR(2) REFERENCES departamentos(id_departamento),
    nombre TEXT NOT NULL,
    es_capital BOOLEAN DEFAULT FALSE,
    geom GEOMETRY(MULTIPOLYGON, 4326)
);

CREATE TABLE IF NOT EXISTS categorias (
    id_categoria BIGSERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    icono TEXT
);

CREATE TABLE IF NOT EXISTS entidades (
    id_entidad BIGSERIAL PRIMARY KEY,
    id_categoria BIGINT REFERENCES categorias(id_categoria),
    id_municipio VARCHAR(5) REFERENCES municipios(id_municipio),
    nombre TEXT NOT NULL,
    descripcion TEXT,
    es_oficial BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ubicaciones (
    id_ubicacion BIGSERIAL PRIMARY KEY,
    id_entidad BIGINT REFERENCES entidades(id_entidad) ON DELETE CASCADE,
    direccion TEXT,
    codigo_postal TEXT,
    lat NUMERIC,
    lon NUMERIC,
    geom GEOMETRY(POINT, 4326)
);

CREATE TABLE IF NOT EXISTS telefonos (
    id_telefono BIGSERIAL PRIMARY KEY,
    id_entidad BIGINT REFERENCES entidades(id_entidad) ON DELETE CASCADE,
    numero TEXT NOT NULL,
    tipo TEXT, -- celular, fijo, emergencias
    es_principal BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS enlaces_oficiales (
    id_enlace BIGSERIAL PRIMARY KEY,
    id_entidad BIGINT REFERENCES entidades(id_entidad) ON DELETE CASCADE,
    url TEXT NOT NULL,
    tipo TEXT, -- web, facebook, twitter, sede_electronica
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS horarios (
    id_horario BIGSERIAL PRIMARY KEY,
    id_entidad BIGINT REFERENCES entidades(id_entidad) ON DELETE CASCADE,
    dia_semana INTEGER NOT NULL, -- 0-6 (0=Lunes)
    hora_apertura TIME,
    hora_cierre TIME,
    es_24_horas BOOLEAN DEFAULT FALSE,
    esta_cerrado BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS servicios (
    id_servicio BIGSERIAL PRIMARY KEY,
    id_entidad BIGINT REFERENCES entidades(id_entidad) ON DELETE CASCADE,
    nombre TEXT NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS tramites (
    id_tramite BIGSERIAL PRIMARY KEY,
    id_entidad BIGINT REFERENCES entidades(id_entidad) ON DELETE CASCADE,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    costo NUMERIC DEFAULT 0,
    url_tramite TEXT,
    es_en_linea BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS noticias (
    id_noticia BIGSERIAL PRIMARY KEY,
    id_entidad BIGINT REFERENCES entidades(id_entidad) ON DELETE CASCADE,
    titulo TEXT NOT NULL,
    contenido TEXT NOT NULL,
    url_fuente TEXT,
    fecha_publicacion TIMESTAMP
);

CREATE TABLE IF NOT EXISTS capas_geograficas (
    id_capa BIGSERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL, -- WMS, WFS, GeoJSON
    url_servicio TEXT NOT NULL,
    parametros JSONB,
    activa BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_municipios_geom ON municipios USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_ubicaciones_geom ON ubicaciones USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_entidades_nombre ON entidades USING GIN (to_tsvector('spanish', nombre));
CREATE INDEX IF NOT EXISTS idx_tramites_nombre ON tramites USING GIN (to_tsvector('spanish', nombre));

-- TABLA DE DENUNCIAS CIUDADANAS (PIPAC V2)
CREATE TABLE IF NOT EXISTS denuncias_ciudadanas (
    id_denuncia     BIGSERIAL PRIMARY KEY,
    tipo_delito     TEXT NOT NULL,          -- Robo, Homicidio, Extorsión, Acoso, Otro
    descripcion     TEXT NOT NULL,
    ciudad          TEXT NOT NULL,
    departamento    TEXT,
    barrio          TEXT,
    lat             NUMERIC,
    lon             NUMERIC,
    geom            GEOMETRY(POINT, 4326),
    es_anonima      BOOLEAN DEFAULT TRUE,
    nombre_denunciante TEXT,
    contacto        TEXT,                   -- email o teléfono (opcional)
    estado          TEXT DEFAULT 'RECIBIDA', -- RECIBIDA, EN_REVISION, CERRADA
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_denuncias_geom     ON denuncias_ciudadanas USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_denuncias_tipo      ON denuncias_ciudadanas (tipo_delito);
CREATE INDEX IF NOT EXISTS idx_denuncias_created   ON denuncias_ciudadanas (created_at DESC);


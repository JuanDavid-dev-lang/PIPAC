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


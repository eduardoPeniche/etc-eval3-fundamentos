-- Activar llaves foráneas en SQLite
PRAGMA foreign_keys = ON;

-- Tabla de ciudades (dimensión)
CREATE TABLE IF NOT EXISTS dim_city (
    city_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    city_name   TEXT NOT NULL,
    country     TEXT NOT NULL,
    lat         REAL NOT NULL,
    lon         REAL NOT NULL,

    UNIQUE(city_name, country)
);

-- Tabla de contaminación del aire (hechos)
CREATE TABLE IF NOT EXISTS fact_air_pollution (
    pollution_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id             INTEGER NOT NULL,
    dt                  INTEGER NOT NULL,  -- Unix timestamp UTC

    -- Índice de calidad del aire
    aqi                 INTEGER NOT NULL,  -- 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor

    -- Concentraciones de contaminantes (μg/m³)
    co                  REAL,              -- Monóxido de carbono
    no                  REAL,              -- Monóxido de nitrógeno
    no2                 REAL,              -- Dióxido de nitrógeno
    o3                  REAL,              -- Ozono
    so2                 REAL,              -- Dióxido de azufre
    pm2_5               REAL,              -- Partículas finas PM2.5
    pm10                REAL,              -- Partículas gruesas PM10
    nh3                 REAL,              -- Amoníaco

    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (city_id) REFERENCES dim_city(city_id)
);

-- Índice para acelerar consultas por ciudad y tiempo
CREATE INDEX IF NOT EXISTS idx_fact_air_pollution_city_dt
    ON fact_air_pollution (city_id, dt);

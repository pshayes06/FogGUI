CREATE TABLE flights (
    id          SERIAL PRIMARY KEY,
    started_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at    TIMESTAMP,
    label       TEXT
);

CREATE TABLE readings (
    id          SERIAL PRIMARY KEY,
    flight_id   INTEGER NOT NULL REFERENCES flights(id),
    recorded_at TIMESTAMP,
    uptime_s    REAL,
    altitude_m  REAL,
    pressure_mb REAL,
    temperature_c REAL,
    humidity_pct  REAL,
    raw_line    TEXT NOT NULL
);

CREATE INDEX idx_readings_flight   ON readings(flight_id);
CREATE INDEX idx_readings_altitude ON readings(flight_id, altitude_m);

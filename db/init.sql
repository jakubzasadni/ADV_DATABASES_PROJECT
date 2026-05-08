CREATE TABLE IF NOT EXISTS earthquakes (
    id          VARCHAR(20) PRIMARY KEY,
    time        TIMESTAMPTZ NOT NULL,
    magnitude   FLOAT,
    mag_type    VARCHAR(10),
    place       TEXT,
    latitude    FLOAT NOT NULL,
    longitude   FLOAT NOT NULL,
    depth       FLOAT,
    status      VARCHAR(20),
    alert       VARCHAR(10),
    tsunami     BOOLEAN DEFAULT FALSE,
    significance INTEGER,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_earthquakes_time       ON earthquakes (time DESC);
CREATE INDEX IF NOT EXISTS idx_earthquakes_magnitude  ON earthquakes (magnitude);
CREATE INDEX IF NOT EXISTS idx_earthquakes_alert      ON earthquakes (alert);

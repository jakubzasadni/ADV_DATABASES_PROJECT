import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

UPSERT_SQL = """
INSERT INTO earthquakes (id, time, magnitude, mag_type, place, latitude, longitude, depth, status, alert, tsunami, significance, updated_at)
VALUES %s
ON CONFLICT (id) DO UPDATE SET
    magnitude   = EXCLUDED.magnitude,
    mag_type    = EXCLUDED.mag_type,
    place       = EXCLUDED.place,
    status      = EXCLUDED.status,
    alert       = EXCLUDED.alert,
    tsunami     = EXCLUDED.tsunami,
    significance= EXCLUDED.significance,
    updated_at  = EXCLUDED.updated_at
"""

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME", "earthquakes"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )

def upsert_events(events: list[dict]) -> int:
    if not events:
        return 0
    rows = [
        (
            e["id"], e["time"], e["magnitude"], e["mag_type"], e["place"],
            e["latitude"], e["longitude"], e["depth"], e["status"],
            e["alert"], e["tsunami"], e["significance"], e["updated_at"],
        )
        for e in events
    ]
    with get_conn() as conn, conn.cursor() as cur:
        execute_values(cur, UPSERT_SQL, rows)
    return len(rows)

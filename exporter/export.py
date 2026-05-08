"""
Eksportuje dane z PostgreSQL do JSON-ów w docs/data/ dla GitHub Pages.
Uruchom: python export.py
"""
import json
import os
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "../docs/data")


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME", "earthquakes"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def export_earthquakes(conn, limit: int = 5000):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, time, magnitude, mag_type, place,
                   latitude, longitude, depth, status,
                   alert, tsunami, significance
            FROM earthquakes
            WHERE time >= NOW() - INTERVAL '365 days'
            ORDER BY time DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
    data = []
    for r in rows:
        row = dict(r)
        row["time"] = row["time"].isoformat()
        data.append(row)
    return data


def export_stats(conn):
    stats = {}
    with conn.cursor() as cur:
        # dzienne liczby zdarzeń z ostatnich 90 dni
        cur.execute("""
            SELECT DATE(time) AS day, COUNT(*) AS count
            FROM earthquakes
            WHERE time >= NOW() - INTERVAL '90 days'
            GROUP BY day ORDER BY day
        """)
        stats["daily_counts"] = [{"day": str(r["day"]), "count": r["count"]} for r in cur.fetchall()]

        # rozkład magnitudy
        cur.execute("""
            SELECT FLOOR(magnitude) AS bucket, COUNT(*) AS count
            FROM earthquakes
            WHERE magnitude IS NOT NULL
              AND time >= NOW() - INTERVAL '365 days'
            GROUP BY bucket ORDER BY bucket
        """)
        stats["magnitude_distribution"] = [{"bucket": float(r["bucket"]), "count": r["count"]} for r in cur.fetchall()]

        # top 10 najsilniejszych
        cur.execute("""
            SELECT id, time, magnitude, place, latitude, longitude
            FROM earthquakes
            WHERE time >= NOW() - INTERVAL '365 days'
            ORDER BY magnitude DESC NULLS LAST
            LIMIT 10
        """)
        stats["top10"] = [dict(r) | {"time": r["time"].isoformat()} for r in cur.fetchall()]

        # podsumowanie
        cur.execute("""
            SELECT COUNT(*) AS total,
                   AVG(magnitude) AS avg_mag,
                   MAX(magnitude) AS max_mag,
                   SUM(tsunami::int) AS tsunami_count
            FROM earthquakes
            WHERE time >= NOW() - INTERVAL '365 days'
        """)
        row = dict(cur.fetchone())
        stats["summary"] = {k: float(v) if v is not None else None for k, v in row.items()}

    return stats


def write_json(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, default=str)
    print(f"Written: {path} ({os.path.getsize(path) // 1024} KB)")


if __name__ == "__main__":
    conn = get_conn()
    write_json(f"{OUTPUT_DIR}/earthquakes.json", export_earthquakes(conn))
    write_json(f"{OUTPUT_DIR}/stats.json", export_stats(conn))
    write_json(f"{OUTPUT_DIR}/meta.json", {"exported_at": datetime.now(tz=timezone.utc).isoformat()})
    conn.close()
    print("Export complete.")

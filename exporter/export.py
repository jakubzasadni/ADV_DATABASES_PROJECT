"""
Eksportuje dane z PostgreSQL do JSON-ów w docs/data/ dla GitHub Pages.
Uruchom: python export.py
"""
import json
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from sqlalchemy import Integer, cast, create_engine, func, select
from sqlalchemy.orm import Session

from models import Earthquake

load_dotenv()
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "../docs/data")


def _build_url() -> str:
    return (
        f"postgresql+psycopg2://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', 'postgres')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', 5432)}/"
        f"{os.getenv('DB_NAME', 'earthquakes')}"
    )


def export_earthquakes(session: Session, limit: int = 5000) -> list[dict]:
    stmt = select(Earthquake).order_by(Earthquake.time.desc()).limit(limit)
    rows = session.scalars(stmt).all()
    return [
        {
            "id": r.id,
            "time": r.time.isoformat(),
            "magnitude": r.magnitude,
            "mag_type": r.mag_type,
            "place": r.place,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "depth": r.depth,
            "status": r.status,
            "alert": r.alert,
            "tsunami": r.tsunami,
            "significance": r.significance,
        }
        for r in rows
    ]


def export_stats(session: Session) -> dict:
    max_time = session.scalar(select(func.max(Earthquake.time)))
    cutoff = max_time - timedelta(days=90)

    # dzienne liczby zdarzeń (ostatnie 90 dni danych w bazie)
    daily_stmt = (
        select(func.date(Earthquake.time).label("day"), func.count().label("count"))
        .where(Earthquake.time >= cutoff)
        .group_by(func.date(Earthquake.time))
        .order_by(func.date(Earthquake.time))
    )
    daily = session.execute(daily_stmt).all()

    # rozkład magnitudy (wszystkie dane)
    mag_stmt = (
        select(func.floor(Earthquake.magnitude).label("bucket"), func.count().label("count"))
        .where(Earthquake.magnitude.is_not(None))
        .group_by(func.floor(Earthquake.magnitude))
        .order_by(func.floor(Earthquake.magnitude))
    )
    mag_dist = session.execute(mag_stmt).all()

    # top 10 najsilniejszych (wszystkie dane)
    top10_stmt = (
        select(Earthquake)
        .where(Earthquake.magnitude.is_not(None))
        .order_by(Earthquake.magnitude.desc())
        .limit(10)
    )
    top10 = session.scalars(top10_stmt).all()

    # podsumowanie (wszystkie dane)
    summary_stmt = select(
        func.count().label("total"),
        func.avg(Earthquake.magnitude).label("avg_mag"),
        func.max(Earthquake.magnitude).label("max_mag"),
        func.sum(cast(Earthquake.tsunami, Integer)).label("tsunami_count"),
    )
    row = session.execute(summary_stmt).one()

    return {
        "daily_counts": [{"day": str(r.day), "count": r.count} for r in daily],
        "magnitude_distribution": [{"bucket": float(r.bucket), "count": r.count} for r in mag_dist],
        "top10": [
            {
                "id": r.id,
                "time": r.time.isoformat(),
                "magnitude": r.magnitude,
                "place": r.place,
                "latitude": r.latitude,
                "longitude": r.longitude,
            }
            for r in top10
        ],
        "summary": {k: float(v) if v is not None else None for k, v in row._mapping.items()},
    }


def write_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, default=str)
    print(f"Written: {path} ({os.path.getsize(path) // 1024} KB)")


if __name__ == "__main__":
    engine = create_engine(_build_url())
    with Session(engine) as session:
        write_json(f"{OUTPUT_DIR}/earthquakes.json", export_earthquakes(session))
        write_json(f"{OUTPUT_DIR}/stats.json", export_stats(session))
    write_json(f"{OUTPUT_DIR}/meta.json", {"exported_at": datetime.now(tz=timezone.utc).isoformat()})
    print("Export complete.")

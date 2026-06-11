import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from models import Base, Earthquake

load_dotenv()


def _build_url() -> str:
    return (
        f"postgresql+psycopg2://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', 'postgres')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', 5432)}/"
        f"{os.getenv('DB_NAME', 'earthquakes')}"
    )


engine = create_engine(_build_url())
Base.metadata.create_all(engine)


def upsert_events(events: list[dict]) -> int:
    if not events:
        return 0

    rows = [
        {
            "id": e["id"],
            "time": e["time"],
            "magnitude": e["magnitude"],
            "mag_type": e["mag_type"],
            "place": e["place"],
            "latitude": e["latitude"],
            "longitude": e["longitude"],
            "depth": e["depth"],
            "status": e["status"],
            "alert": e["alert"],
            "tsunami": e["tsunami"],
            "significance": e["significance"],
            "updated_at": e["updated_at"],
        }
        for e in events
    ]

    stmt = pg_insert(Earthquake).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "magnitude": stmt.excluded.magnitude,
            "mag_type": stmt.excluded.mag_type,
            "place": stmt.excluded.place,
            "status": stmt.excluded.status,
            "alert": stmt.excluded.alert,
            "tsunami": stmt.excluded.tsunami,
            "significance": stmt.excluded.significance,
            "updated_at": stmt.excluded.updated_at,
        },
    )

    with Session(engine) as session:
        session.execute(stmt)
        session.commit()

    return len(rows)

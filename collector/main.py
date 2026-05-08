"""
Pobiera dane z USGS API i zapisuje do PostgreSQL.
Tryb historyczny: python main.py --from 2020-01-01 --to 2024-12-31
Tryb live:        python main.py --live   (pobiera ostatnie 7 dni co godzinę)
"""
import argparse
import time
from datetime import datetime, timedelta, timezone

from usgs_api import fetch_events
from db import upsert_events

CHUNK_DAYS = 30


def collect_range(start: datetime, end: datetime):
    cursor = start
    total = 0
    while cursor < end:
        chunk_end = min(cursor + timedelta(days=CHUNK_DAYS), end)
        print(f"Fetching {cursor.date()} → {chunk_end.date()} ...", end=" ", flush=True)
        events = fetch_events(cursor, chunk_end)
        saved = upsert_events(events)
        print(f"{saved} events")
        total += saved
        cursor = chunk_end
    print(f"Done. Total upserted: {total}")


def live_loop(interval_sec: int = 3600):
    print(f"Live mode: collecting every {interval_sec}s")
    while True:
        end = datetime.now(tz=timezone.utc)
        start = end - timedelta(days=7)
        collect_range(start, end)
        time.sleep(interval_sec)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", dest="date_from", help="Start date YYYY-MM-DD")
    parser.add_argument("--to",   dest="date_to",   help="End date YYYY-MM-DD")
    parser.add_argument("--live", action="store_true", help="Live collection loop")
    args = parser.parse_args()

    if args.live:
        live_loop()
    elif args.date_from and args.date_to:
        start = datetime.fromisoformat(args.date_from).replace(tzinfo=timezone.utc)
        end   = datetime.fromisoformat(args.date_to).replace(tzinfo=timezone.utc)
        collect_range(start, end)
    else:
        # domyślnie: ostatnie 30 dni
        end = datetime.now(tz=timezone.utc)
        collect_range(end - timedelta(days=30), end)

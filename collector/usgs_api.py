from datetime import datetime, timezone
import requests

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
LIMIT = 20000

def fetch_events(start: datetime, end: datetime) -> list[dict]:
    params = {
        "format": "geojson",
        "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "endtime": end.strftime("%Y-%m-%dT%H:%M:%S"),
        "limit": LIMIT,
        "orderby": "time-asc",
    }
    resp = requests.get(USGS_URL, params=params, timeout=60)
    resp.raise_for_status()
    features = resp.json().get("features", [])
    return [_parse(f) for f in features]

def _parse(feature: dict) -> dict:
    p = feature["properties"]
    c = feature["geometry"]["coordinates"]
    ts_ms = p.get("time") or 0
    upd_ms = p.get("updated") or ts_ms
    return {
        "id":           feature["id"],
        "time":         datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc),
        "magnitude":    p.get("mag"),
        "mag_type":     p.get("magType"),
        "place":        p.get("place"),
        "longitude":    c[0],
        "latitude":     c[1],
        "depth":        c[2],
        "status":       p.get("status"),
        "alert":        p.get("alert"),
        "tsunami":      bool(p.get("tsunami")),
        "significance": p.get("sig"),
        "updated_at":   datetime.fromtimestamp(upd_ms / 1000, tz=timezone.utc),
    }

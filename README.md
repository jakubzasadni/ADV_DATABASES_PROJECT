# Global Earthquake Monitor

Advanced Databases course project — data collection, storage and visualization of worldwide seismic events.

**Team**: Dawid Świgut · Krzysztof Witek · Jakub Zasadni

**Live dashboard**: [jakubzasadni.github.io/ADV_DATABASES_PROJECT](https://jakubzasadni.github.io/ADV_DATABASES_PROJECT)

---

## Architecture

```
USGS Earthquake API
        │
        ▼
  Python Collector  ──►  PostgreSQL (Docker)
                                │
                         Python Exporter
                                │
                                ▼
                      docs/data/*.json  ──►  GitHub Pages (static dashboard)
```

## Stack

| Layer | Technology |
|-------|-----------|
| Database | PostgreSQL 16 |
| Collector | Python 3.12, psycopg2, requests |
| Exporter | Python 3.12, psycopg2 |
| Dashboard | HTML/CSS/JS, Plotly.js, Leaflet.js |
| Hosting | GitHub Pages (`docs/`) |

## Quick start

```bash
cp .env.example .env

# Start database + collector (fetches last 30 days by default)
docker compose up -d db
docker compose run --rm collector python main.py --from 2024-01-01 --to 2024-12-31

# Export data to docs/data/
docker compose --profile export run --rm exporter

# Or run locally
cd collector && pip install -r requirements.txt
python main.py --from 2024-01-01 --to 2024-12-31

cd ../exporter && pip install -r requirements.txt
python export.py
```

Open `docs/index.html` in a browser or visit the GitHub Pages URL.

## Dashboard filters

1. Date range
2. Min / max magnitude
3. Max depth (km)
4. Alert level (green / yellow / orange / red)
5. Tsunami warning (yes / no)
6. Location text search
7. *(map: click a marker for full event details)*

## Data source

[USGS Earthquake Catalog API](https://earthquake.usgs.gov/fdsnws/event/1/) — public, no API key required.

Fields stored: `id`, `time`, `magnitude`, `mag_type`, `place`, `latitude`, `longitude`, `depth`, `status`, `alert`, `tsunami`, `significance`.

## Project structure

```
├── db/             PostgreSQL schema (init.sql)
├── collector/      Python: USGS API → PostgreSQL
├── exporter/       Python: PostgreSQL → docs/data/*.json
├── docs/           GitHub Pages root
│   ├── index.html
│   ├── css/style.css
│   ├── js/app.js
│   └── data/       Generated JSON (earthquakes, stats, meta)
└── docker-compose.yml
```

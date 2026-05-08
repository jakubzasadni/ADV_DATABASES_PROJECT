# Global Earthquake Monitor - Advanced Databases Project

## Project Overview

System do pobierania, przechowywania i wizualizacji danych sejsmicznych z całego świata.

**Zespół**: Dawid Świgut, Krzysztof Witek, Jakub Zasadni  
**Kurs**: Advanced Databases

## Stack technologiczny

- **Baza danych**: PostgreSQL (docker-compose, lokalnie)
- **Kolektor danych**: Python (httpx/requests, psycopg2/SQLAlchemy)
- **Źródło danych**: USGS Earthquake Catalog API (GeoJSON)
- **Dashboard**: Statyczny HTML/CSS/JS (GitHub Pages) - Plotly.js + Leaflet.js
- **Eksport danych**: Python skrypt generujący JSON z PostgreSQL → `docs/data/`
- **CI/CD**: GitHub Actions - automatyczny eksport + deploy na GitHub Pages

## Architektura

```
PostgreSQL (docker) ←── Python collector (USGS API)
        ↓
Python export script → docs/data/*.json
        ↓
GitHub Pages (docs/) → statyczny dashboard HTML/JS
```

GitHub Pages serwuje folder `docs/`. Dashboard fetchuje lokalne pliki JSON (pre-generated).

## Struktura projektu

```
/
├── db/
│   └── init.sql              # Schema PostgreSQL
├── collector/
│   ├── main.py               # Entry point (pobiera dane z USGS → PostgreSQL)
│   ├── usgs_api.py           # Klient USGS API
│   ├── db.py                 # Połączenie z PostgreSQL, UPSERT
│   └── requirements.txt
├── exporter/
│   ├── export.py             # Eksportuje dane z PostgreSQL → docs/data/*.json
│   └── requirements.txt
├── docs/                     # GitHub Pages root
│   ├── index.html            # Dashboard
│   ├── css/style.css
│   ├── js/app.js             # Logika: filtry, wykresy Plotly.js, mapa Leaflet
│   └── data/                 # Generowane JSON-y (gitignored lub commitowane)
│       ├── earthquakes.json
│       └── stats.json
├── docker-compose.yml
└── .gitignore
```

## Źródła danych USGS

- API endpoint: `https://earthquake.usgs.gov/fdsnws/event/1/query`
- GeoJSON feeds: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php`
- Format: GeoJSON

## Schema bazy danych

Tabela `earthquakes`:
| Kolumna | Typ | Opis |
|---------|-----|------|
| id | VARCHAR (PK) | USGS event ID |
| time | TIMESTAMPTZ | Czas zdarzenia |
| magnitude | FLOAT | Magnituda |
| place | TEXT | Opis lokalizacji |
| latitude | FLOAT | Szerokość geograficzna |
| longitude | FLOAT | Długość geograficzna |
| depth | FLOAT | Głębokość (km) |
| status | VARCHAR | Status zdarzenia (reviewed/automatic) |
| mag_type | VARCHAR | Typ magnitudy (ml, mw, mb...) |
| alert | VARCHAR | Poziom alertu (green/yellow/orange/red) |
| tsunami | BOOLEAN | Czy mogło wywołać tsunami |
| significance | INTEGER | Wskaźnik znaczenia zdarzenia |
| updated_at | TIMESTAMPTZ | Czas ostatniej aktualizacji rekordu |

## Filtry dashboardu (min. 5 wymaganych)

1. Zakres dat (date range)
2. Min/max magnituda
3. Głębokość trzęsienia
4. Region/lokalizacja (text search lub bounding box)
5. Status zdarzenia
6. Poziom alertu
7. Tsunami (tak/nie)

## Typy analiz

- **Szeregi czasowe**: liczba zdarzeń dziennie/tygodniowo/miesięcznie
- **Ilościowa**: rozkład magnitudy, głębokości, histogram
- **Przestrzenna**: mapa świata z punktami zdarzeń (Plotly mapbox)

## Zasady dla AI

1. PostgreSQL: używaj UPSERT (`ON CONFLICT (id) DO UPDATE`) - USGS aktualizuje zdarzenia
2. Kolektor: pobieraj dane partiami po 30 dni, max 20000 rekordów na zapytanie USGS API
3. Nie używaj ORM do bulk insertów - `executemany` z psycopg2 dla wydajności
4. Zmienne środowiskowe przez `.env` (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
5. Docker: baza na named volume, kolektor i exporter jako osobne serwisy
6. Dashboard (GitHub Pages): czysty JS bez frameworków, Plotly.js CDN + Leaflet.js CDN
7. Filtry w dashboardzie działają client-side na załadowanych JSON-ach (nie fetchują za każdym razem)
8. JSON eksport: `earthquakes.json` = lista ostatnich N zdarzeń, `stats.json` = agregaty do wykresów

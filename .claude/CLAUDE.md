# Global Earthquake Monitor - Advanced Databases Project

## Project Overview

System do pobierania, przechowywania i wizualizacji danych sejsmicznych z całego świata.

**Zespół**: Dawid Świgut, Krzysztof Witek, Jakub Zasadni  
**Kurs**: Advanced Databases

## Stack technologiczny

- **Baza danych**: PostgreSQL + PostGIS (dane przestrzenne)
- **Kolektor danych**: Python (APScheduler, httpx/requests, SQLAlchemy)
- **Źródło danych**: USGS Earthquake Catalog API (GeoJSON)
- **Dashboard**: Python Dash (plotly) lub Streamlit
- **Środowisko**: Docker Compose (PostgreSQL + kolektor + dashboard)

## Struktura projektu

```
/
├── db/
│   ├── init.sql          # Schema PostgreSQL
│   └── migrations/       # Ewentualne migracje Alembic
├── collector/
│   ├── main.py           # Entry point kolektora (scheduler)
│   ├── usgs_api.py       # Klient USGS API
│   ├── models.py         # SQLAlchemy modele
│   └── requirements.txt
├── dashboard/
│   ├── app.py            # Główna aplikacja Dash/Streamlit
│   ├── components/       # Komponenty UI
│   └── requirements.txt
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

1. PostgreSQL: używaj UPSERT (`ON CONFLICT DO UPDATE`) przy wstawianiu danych, bo USGS aktualizuje zdarzenia
2. Kolektor: pobieraj dane partiami (np. po 30 dni) żeby nie przekroczyć limitów USGS API (max 20000 rekordów na zapytanie)
3. Dashboard: filtry reagują real-time (Dash callbacks), mapa jako Plotly scatter_mapbox
4. Docker: wszystkie serwisy przez docker-compose, baza na wolumenie named
5. Nie używaj ORM do bulk insertów - preferuj `executemany` / `copy_from` dla wydajności
6. Zmienne środowiskowe przez `.env` file (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)

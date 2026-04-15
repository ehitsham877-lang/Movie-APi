# Movie API (IMDb-style) – FastAPI starter

This repo is a **starter scaffold** for a movie / TV database API you can publish on RapidAPI.
It’s designed around **pluggable data providers** (TMDb, TVDB, Wikidata, your own catalog, etc.) so you can build a “market-level” API without hard-coding a single source.

## Important licensing note (read first)

If you want “cheaper than IMDb licensing”, you still must **license or use permitted sources**:
- **Do not scrape IMDb** or repackage IMDb content unless you have rights and comply with their terms.
- Many popular APIs (e.g., TMDb/TVDB/JustWatch) have **redistribution/resale restrictions**. RapidAPI can be considered resale. Verify the ToS and attribution requirements.
- Trailers usually come from **YouTube** (or other platforms) and have their own ToS; a safe pattern is to store and return **video IDs/URLs**, not rehost videos.

This project ships with a **Mock provider** so you can develop endpoints without any licensed data.

## What’s included

- FastAPI app with versioned routes (`/v1`)
- Provider interface + `MockProvider`
- Endpoints: search, title details, credits (cast/crew), ratings, trailers
- Simple API-key auth (optional)

## Quickstart

1) Create a venv and install deps:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

2) Configure env:
```powershell
Copy-Item .env.example .env
```

Then set `TMDB_API_KEY` inside `.env` (do not commit it).

3) Run:
```powershell
uvicorn app.main:app --reload
# or (repo-root shortcut):
uvicorn main:app --reload
```

Open:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Next steps to reach “market-level”

- Pick sources + confirm licensing for **RapidAPI redistribution**
- Add a DB (Postgres) + caching (Redis) + background sync jobs
- Implement a real provider (TMDb/Wikidata/etc.) behind `Provider` interface
- Add de-duplication across sources (“canonical title IDs”)
- Add rate limits, observability, and paid-plan quotas

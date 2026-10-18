# Live Here Before You Buy

Web app that shows home buyers what daily life in a specific unit feels like before they buy, and matches them to the unit that fits their life. Sime Darby Property University Hackathon — "Township of Tomorrow". Target: Serenia City, Sepang — precinct = Jalan Aman Serenia 17/9 + 17/8 (Serenia Anisa neighbourhood), ~20 mocked units, 17/9 fronting the Persiaran Bandar Serenia main road/roundabout. See `data/raw/location_notes.md` for the geocoding and precinct bbox.

Out of scope for the hackathon: real SDP data, auth, payments, mobile app.

## Stack

Frontend: React + Vite + Tailwind, MapLibre GL (extruded precinct), three.js + SunCalc (unit close-up shadows).
Backend: FastAPI.
Data prep: Python (osmnx, overpy, pvlib, trimesh, shapely, geopandas, rasterio) in `pipeline/`, run once / on change, not at request time.
AI: Gemini API for life-fit matching and ask-the-unit chat.

## Data flow

`data/precinct.geojson` (hand-traced unit footprints) -> `pipeline/build.py` runs sun/noise/flood/commute/amenities -> `data/processed/units_livability.json` (one record per unit) -> backend serves it, frontend renders it.

Record shape and full factor table are in the hackathon handoff doc; `pipeline/build.py` has a TODO marking where each module's output plugs into the record.

## Conventions

- Python: type hints, small pure functions. Every tunable threshold lives in `pipeline/config.py`, never hardcoded inline.
- Every modelled output (noise, flood, heat rating) carries `"indicative": true` and must be labelled as an estimate in the UI. Never state these as fact.
- Never commit API keys — `.env` only, keep `.env.example` in sync.
- Cache every paid API call to disk (commute -> `data/raw/commute_cache.json`). Never call Google Routes per-unit or per-request — once per precinct centroid per destination.
- Gemini chat/match responses must only cite numbers present in the unit's own data record. No invented numbers.
- Tests: pytest for pipeline maths (attenuation, energy sum, scoring normalisation) under `pipeline/`; Vitest for key frontend components.
- Framing: present results constructively (helping buyers choose the right unit), never as "this township has problems" — judges are from Sime Darby Property.

## API (FastAPI, see backend/routers/)

- `GET /units` — list units, summary ratings + geometry
- `GET /units/{unit_id}` — full livability record
- `GET /units/compare?ids=A-01,B-12` — side-by-side records
- `POST /match` — `{description}` -> ranked units with Gemini explanations
- `POST /units/{unit_id}/chat` — `{message, history}` -> grounded answer
- `POST /commute/custom` — `{destination}` -> cached commute times

## Current state

Scaffold only — routers, services and pipeline modules are stubs with `TODO`/`NotImplementedError` markers. Milestone order (see handoff doc §11): geocode + pick precinct, trace `precinct.geojson`, sun model + shadow slider (most visual, do early), map, Gemini match/chat, commute, noise, flood, polish.

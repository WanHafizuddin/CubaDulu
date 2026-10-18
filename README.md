# Live Here Before You Buy

Shows home buyers what daily life in a specific unit feels like before they buy, and matches them to the unit that fits their life. Built for the Sime Darby Property University Hackathon ("Township of Tomorrow"), targeting Serenia City, Sepang.

> Brochures show how a home looks. We show how it lives.

See [CLAUDE.md](CLAUDE.md) for the full project spec (scope, data model, algorithms, API, milestones).

## Setup

### Pipeline (Python)
```bash
cd pipeline
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
```

### Backend (FastAPI)
```bash
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in GEMINI_API_KEY, GOOGLE_MAPS_API_KEY
uvicorn main:app --reload
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Repo structure

```
data/           hand-traced precinct.geojson, raw OSM/DEM extracts, processed output
pipeline/       Python data prep (sun, noise, flood, commute, amenities) -> data/processed/units_livability.json
backend/        FastAPI: units/match/chat/commute endpoints, Gemini + scoring services
frontend/       React + Vite + Tailwind: map, unit view, compare, match pages
```

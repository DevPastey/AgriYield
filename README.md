# AgriYield-API

Precision irrigation and fertilizer recommendation engine. Farmers (or agronomists)
enter a crop type, soil texture, growth stage, and location; the system pulls a live
weather forecast for that location and turns it into a 7-day irrigation and NPK
fertilizer plan, with plain-language reasoning for each recommendation.

## The problem

Most smallholder farmers apply fertilizer and irrigation on a fixed, uniform
schedule regardless of soil type or upcoming weather. That wastes money, wastes
water, and can damage soil over time. This project generates localized,
data-driven recommendations instead.

## Architecture

```
AgriYield-API/
├── backend/          FastAPI service — API, weather integration, agronomy engine
│   └── app/
│       ├── api/routes/       HTTP endpoints
│       ├── core/              config
│       ├── schemas/           Pydantic request/response models
│       ├── services/          business logic (weather client + agronomy engines)
│       └── data/              reference tables (Kc values, NPK baselines, etc.)
└── frontend/         Next.js dashboard — form, weather strip, 7-day calendar chart
    ├── app/
    ├── components/
    └── lib/
```

**Data flow:** frontend form → `POST /api/v1/recommendations` → backend fetches live
weather from OpenWeatherMap → agronomy engines compute evapotranspiration, irrigation
need, and NPK blend → response renders as a 7-day plan with a water-balance chart.

## What's implemented vs. what's left for you

This scaffold wires up everything *except* the agronomy decision logic itself —
that's the part that should demonstrate your own domain expertise.

**Fully implemented:**
- FastAPI app, routing, CORS, config (`backend/app/main.py`, `core/`, `api/`)
- Pydantic request/response schemas (`backend/app/schemas/`)
- OpenWeatherMap integration with retries + caching (`backend/app/services/weather_service.py`)
- Next.js dashboard: input form, weather strip, 7-day chart (recharts), reasoning cards
- Typed frontend API client (`frontend/lib/api.ts`)
- Docker Compose setup for running both services together

**Left as `TODO` for you to implement** (see docstrings in each file for guidance):
- `backend/app/services/evapotranspiration.py` — FAO-56 Penman-Monteith / Hargreaves ET₀, crop coefficient (Kc) lookup
- `backend/app/services/irrigation_engine.py` — soil moisture bucket model, irrigate/skip decision rule
- `backend/app/services/fertilizer_engine.py` — NPK baseline tables, soil-texture adjustments, application scheduling
- `backend/tests/test_recommendations.py` — test cases scaffolded, assertions to fill in once the above are done

## Getting started

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and add a free OpenWeatherMap API key:
# https://home.openweathermap.org/api_keys
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs` once running.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Dashboard at `http://localhost:3000`.

### Or, with Docker Compose

```bash
cp backend/.env.example backend/.env   # then add your OpenWeatherMap key
docker compose up --build
```

## Roadmap ideas (optional, for later)

- Geocoding lookup (OpenWeatherMap Geo API) so users type a place name instead of lat/lon
- Persist past recommendations per field (adds a database — Postgres via SQLAlchemy fits this stack well)
- Expand crop/soil reference tables beyond the initial demo set
- Swap the free `/forecast` endpoint for One Call 3.0 to get a true 7-8 day outlook plus rain probability

## License

MIT — see LICENSE (add one before publishing, if you want one).

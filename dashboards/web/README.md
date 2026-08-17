# EnviroLens Web Dashboard

React / Next.js dashboard for the EnviroLens FastAPI backend.

## Prerequisites

- Node.js 20+
- Running FastAPI backend (`uvicorn api.main:app --reload`)
- Loaded database (pipeline + risk calculation)

## Setup

```bash
cd dashboards/web
cp .env.local.example .env.local
npm install
```

From repo root, copy map assets (optional):

```bash
make web-maps
```

## Development

```bash
npm run dev
```

Open http://localhost:3001 (or set `PORT` in `.env.local`)

## Pages

| Route | Content |
|-------|---------|
| `/` | Executive overview KPIs **and charts** (risk mix, trends, quality) |
| `/risk` | AP-EHRI rankings, histogram, radar, district bars |
| `/data-quality` | DQ dimension scores and progress bars |
| `/facilities` | Health facility capacity |
| `/metadata` | Dataset catalogue |
| `/map` | Choropleth + interactive Folium map |

## Configuration

| Variable | Description |
|----------|-------------|
| `PORT` | Next.js dev server port (default `3001`) |
| `NEXT_PUBLIC_API_URL` | FastAPI base URL (default `http://localhost:8000`) |
| `NEXT_PUBLIC_API_KEY` | `X-API-Key` header value |
| `API_URL` | Server-side proxy target (used by Next rewrites) |

The dev server proxies `/api-backend/*` to the FastAPI host to avoid CORS issues in some setups.

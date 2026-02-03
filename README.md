# Star Wars API Explorer

REST API + Frontend for exploring the Star Wars universe.

## What is this?

An API that consumes [SWAPI](https://swapi.dev) (Star Wars API) and exposes friendlier endpoints with:
- Pagination, search, and sorting
- Correlated queries (characters from a film, planet residents, etc.)
- API Key authentication
- React frontend with Star Wars theme

## Stack

**Backend**
- Python 3.11 + FastAPI
- httpx (async HTTP client)
- Pydantic v2

**Frontend**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- React Query

**Infrastructure**
- Docker
- GCP Cloud Run

## Quick Start

### Backend

```bash
cd api

# Create virtualenv (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy example .env
cp .env.example .env

# Run dev server
uvicorn src.main:app --reload
```

API available at http://localhost:8000

Docs at http://localhost:8000/docs

### Frontend

```bash
cd web

# Install dependencies
npm install

# Copy example .env
cp .env.example .env

# Run dev server
npm run dev
```

Frontend available at http://localhost:5173

## Project Structure

```
├── api/                    # FastAPI Backend
│   ├── src/
│   │   ├── main.py         # Entrypoint
│   │   ├── config.py       # Configuration
│   │   ├── dependencies.py # DI and auth
│   │   ├── routers/        # Endpoints by resource
│   │   ├── services/       # SWAPI client
│   │   ├── schemas/        # Pydantic models
│   │   └── exceptions/     # Custom errors
│   └── tests/              # pytest tests
├── web/                    # React Frontend
│   └── src/
│       ├── components/     # React components
│       ├── pages/          # Application pages
│       ├── hooks/          # Custom hooks
│       ├── services/       # API client
│       └── types/          # TypeScript types
├── scripts/                # Deployment scripts
└── docs/
    └── GCP_DEPLOY_GUIDE.md # GCP deployment guide
```

## Endpoints

| Resource | Endpoints |
|----------|-----------|
| Characters | `GET /characters`, `GET /characters/{id}`, `GET /characters/{id}/films` |
| Planets | `GET /planets`, `GET /planets/{id}`, `GET /planets/{id}/residents` |
| Starships | `GET /starships`, `GET /starships/{id}`, `GET /starships/{id}/pilots` |
| Films | `GET /films`, `GET /films/{id}`, `GET /films/{id}/characters`, etc. |

All endpoints (except `/health`) require `X-API-Key` header.

## Tests

```bash
cd api
pytest                                  # Run tests
pytest --cov=src --cov-report=html     # With coverage
```

## Docker

```bash
# Build
docker build -t swapi-api ./api

# Run
docker run -p 8000:8000 \
  -e API_KEY=your-secret-key \
  -e CORS_ORIGINS='["http://localhost:5173"]' \
  swapi-api
```

## GCP Deployment

See [docs/GCP_DEPLOY_GUIDE.md](docs/GCP_DEPLOY_GUIDE.md) for complete deployment instructions.

Quick deploy using the automation script:

```bash
export GCP_PROJECT_ID=your-project
export API_KEY=your-secret-key

# Deploy backend only
./scripts/deploy-gcp.sh deploy

# Deploy frontend only
./scripts/deploy-gcp.sh frontend

# Deploy both
./scripts/deploy-gcp.sh all
```

## Environment Variables

### Backend (.env)
```
API_KEY=your-secret-key
SWAPI_BASE_URL=https://swapi.dev/api
LOG_LEVEL=INFO
CACHE_TTL_SECONDS=300
CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_API_KEY=your-secret-key
```

## License

MIT

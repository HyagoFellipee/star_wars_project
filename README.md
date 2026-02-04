# Star Wars API Explorer

REST API + Frontend for exploring the Star Wars universe.

## Live Demo

- **Frontend**: https://storage.googleapis.com/swapi-frontend-swapi-explorer-2024/index.html
- **API**: https://swapi-api-984554052871.us-central1.run.app
- **API Docs**: https://swapi-api-984554052871.us-central1.run.app/docs

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

## Running the Project

### Option 1: Local Development

**Backend**
```bash
cd api
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload
```
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

**Frontend**
```bash
cd web
npm install
cp .env.example .env
npm run dev
```
- Frontend: http://localhost:5173

### Option 2: Docker

```bash
docker compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### Option 3: GCP Deployment

```bash
export GCP_PROJECT_ID=your-project
export API_KEY=your-secret-api-key-here

./scripts/deploy-gcp.sh all
```

See [docs/GCP_DEPLOY_GUIDE.md](docs/GCP_DEPLOY_GUIDE.md) for detailed instructions.

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

## Environment Variables

### Backend (.env)
```
API_KEY=your-secret-api-key-here
SWAPI_BASE_URL=https://swapi.dev/api
LOG_LEVEL=INFO
CACHE_TTL_SECONDS=300
CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_API_KEY=your-secret-api-key-here
```

## License

MIT

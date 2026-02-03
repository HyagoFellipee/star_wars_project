# Star Wars API Explorer

REST API + Frontend for exploring the Star Wars universe, consuming SWAPI.

## Stack
- **Backend**: FastAPI + Python 3.11 + httpx (async)
- **Frontend**: React 18 + TypeScript + Vite + Tailwind
- **Infra**: Docker + GCP Cloud Run
- **Tests**: pytest (backend), vitest (frontend)

## Structure
- `api/` - FastAPI backend
- `web/` - React frontend
- `docs/` - Deployment guides
- `scripts/` - Automation scripts

## Commands

### Backend (api/)
```bash
cd api
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8005   # dev server
pytest -v                                    # tests
pytest --cov=src --cov-report=html           # coverage
```

### Frontend (web/)
```bash
cd web
npm install
npm run dev                            # dev server :5173
npm run build                          # prod build
npm test                               # tests
```

### Docker
```bash
docker build -t swapi-api ./api
docker run -p 8005:8000 -e API_KEY=your-key -e CORS_ORIGINS='["http://localhost:5173"]' swapi-api
```

## Code Standards

### Python
- Type hints on all functions
- Async for external HTTP calls (httpx)
- Custom exceptions in src/exceptions/
- Logging instead of print
- Docstrings only when non-obvious

### TypeScript/React
- Functional components + hooks
- Types in src/types/
- Custom hooks in src/hooks/
- Avoid any, prefer unknown when necessary

### Naming
- Domain-specific descriptive functions: fetch_character_homeworld, not get_data
- Files: snake_case (Python), kebab-case (TS)
- Commits in English, imperative: "add character filtering"

## IMPORTANT

- NEVER hardcode secrets - use environment variables
- ALWAYS run `pytest -v` after backend changes
- ALWAYS run `npm run build` after frontend changes (checks types)
- SWAPI errors must have specific handling (timeout, 404, rate limit)
- `.env` files should NOT be committed (use `.env.example` as reference)

## Environment Variables

### Backend (api/.env)
```
API_KEY=your-secret-api-key
SWAPI_BASE_URL=https://swapi.dev/api
LOG_LEVEL=INFO
CACHE_TTL_SECONDS=300
CORS_ORIGINS=["http://localhost:5173","http://localhost:5175","http://localhost:3000"]
```

### Frontend (web/.env)
```
VITE_API_URL=http://localhost:8005
VITE_API_KEY=your-secret-api-key
```

> **Note**: Adjust backend port and CORS origins as needed.

## Features
1. Endpoints for people, planets, starships, films
2. Filters and sorting
3. Correlated queries (e.g., characters from a film)
4. API Key authentication
5. Unit tests
6. OpenAPI documentation (automatic via FastAPI)

## Key Files
- `api/src/main.py` - FastAPI entrypoint
- `api/src/services/swapi_client.py` - Async SWAPI client (cache, retry, rate limit)
- `api/src/config.py` - Pydantic settings
- `api/tests/conftest.py` - Test fixtures and mocks (respx)
- `web/src/services/api.ts` - Our API client
- `docs/GCP_DEPLOY_GUIDE.md` - GCP deployment guide

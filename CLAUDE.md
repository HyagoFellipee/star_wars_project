# PowerOfData SWAPI Challenge

API REST + Frontend para exploração do universo Star Wars, consumindo a SWAPI.

## Stack
- **Backend**: FastAPI + Python 3.11 + httpx (async)
- **Frontend**: React 18 + TypeScript + Vite + Tailwind
- **Infra**: Docker + GCP Cloud Run
- **Testes**: pytest (backend), vitest (frontend)

## Estrutura
- `api/` - FastAPI backend
- `web/` - React frontend
- `docs/` - Arquitetura e diagramas

## Comandos

### Backend (api/)
```bash
cd api
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8005   # dev server
pytest -v                                    # testes
pytest --cov=src --cov-report=html           # cobertura
```

### Frontend (web/)
```bash
cd web
npm install
npm run dev                            # dev server :5173
npm run build                          # build prod
npm test                               # testes
```

### Docker
```bash
docker build -t swapi-api ./api
docker run -p 8005:8000 -e API_KEY=your-key -e CORS_ORIGINS='["http://localhost:5173"]' swapi-api
```

## Padrões de código

### Python
- Type hints em todas as funções
- Async para chamadas HTTP externas (httpx)
- Exceptions customizadas em src/exceptions/
- Logging ao invés de print
- Docstrings só quando não-óbvio

### TypeScript/React
- Functional components + hooks
- Types em src/types/
- Custom hooks em src/hooks/
- Evite any, prefira unknown quando necessário

### Nomenclatura
- Funções descritivas pro domínio: fetch_character_homeworld, não get_data
- Arquivos snake_case (Python), kebab-case (TS)
- Commits em inglês, imperativo: "add character filtering"

## IMPORTANTE

- NUNCA hardcode secrets - use variáveis de ambiente
- SEMPRE rode `pytest -v` após mudanças no backend (16 testes, todos passando)
- SEMPRE rode `npm run build` após mudanças no frontend (verifica types)
- Erros da SWAPI devem ter tratamento específico (timeout, 404, rate limit)
- TODOs são bem-vindos para marcar melhorias futuras
- Os arquivos `.env` NÃO devem ser commitados (use `.env.example` como referência)

## Variáveis de ambiente

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

> **Nota**: Ajuste a porta do backend e as origens CORS conforme necessário.

## Contexto

Case técnico para PowerOfData. Requisitos principais:
1. Endpoints para people, planets, starships, films
2. Filtros e ordenação
3. Consultas correlacionadas (ex: personagens de um filme)
4. Autenticação via API Key
5. Testes unitários (min 70% cobertura em services)
6. Documentação OpenAPI (automática via FastAPI)

## Arquivos-chave
- `api/src/main.py` - Entrypoint FastAPI
- `api/src/services/swapi_client.py` - Cliente async SWAPI (cache, retry, rate limit)
- `api/src/config.py` - Settings com Pydantic
- `api/tests/conftest.py` - Fixtures e mocks para testes (respx)
- `web/src/services/api.ts` - Cliente da nossa API
- `docs/ARCHITECTURE.md` - Diagrama e decisões

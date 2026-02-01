# PowerOfData SWAPI Challenge

API REST + Frontend para exploração do universo Star Wars.

Case técnico para processo seletivo na PowerOfData.

## O que é isso?

Uma API que consome a [SWAPI](https://swapi.dev) (Star Wars API) e expõe endpoints mais amigáveis, com:
- Paginação, busca e ordenação
- Consultas correlacionadas (personagens de um filme, residentes de um planeta, etc)
- Autenticação via API Key
- Frontend React com tema Star Wars

## Stack

**Backend**
- Python 3.11 + FastAPI
- httpx (cliente HTTP async)
- Pydantic v2

**Frontend**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- React Query

**Infra**
- Docker
- GCP Cloud Run

## Quick Start

### Backend

```bash
cd api

# Criar virtualenv (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Copiar .env de exemplo
cp .env.example .env

# Rodar servidor de dev
uvicorn src.main:app --reload
```

API disponível em http://localhost:8000

Docs em http://localhost:8000/docs

### Frontend

```bash
cd web

# Instalar dependências
npm install

# Copiar .env de exemplo
cp .env.example .env

# Rodar dev server
npm run dev
```

Frontend disponível em http://localhost:5173

## Estrutura

```
├── api/                    # Backend FastAPI
│   ├── src/
│   │   ├── main.py         # Entrypoint
│   │   ├── config.py       # Configurações
│   │   ├── dependencies.py # DI e auth
│   │   ├── routers/        # Endpoints por recurso
│   │   ├── services/       # SWAPI client
│   │   ├── schemas/        # Pydantic models
│   │   └── exceptions/     # Erros customizados
│   └── tests/              # Testes pytest
├── web/                    # Frontend React
│   └── src/
│       ├── components/     # Componentes React
│       ├── pages/          # Páginas da aplicação
│       ├── hooks/          # Custom hooks
│       ├── services/       # API client
│       └── types/          # TypeScript types
└── docs/
    └── ARCHITECTURE.md     # Arquitetura e decisões
```

## Endpoints

| Recurso | Endpoints |
|---------|-----------|
| Characters | `GET /characters`, `GET /characters/{id}`, `GET /characters/{id}/films` |
| Planets | `GET /planets`, `GET /planets/{id}`, `GET /planets/{id}/residents` |
| Starships | `GET /starships`, `GET /starships/{id}`, `GET /starships/{id}/pilots` |
| Films | `GET /films`, `GET /films/{id}`, `GET /films/{id}/characters`, etc |

Todos os endpoints (exceto `/health`) requerem header `X-API-Key`.

## Testes

```bash
cd api
pytest                                  # Rodar testes
pytest --cov=src --cov-report=html     # Com cobertura
```

## Docker

```bash
# Build
docker build -t swapi-api ./api

# Run
docker run -p 8000:8000 -e API_KEY=sua-chave swapi-api
```

## Decisões técnicas interessantes

### Por que httpx e não requests?
O `requests` é síncrono. Quando fazemos várias chamadas à SWAPI (tipo pegar todos os personagens de um filme), seria lento demais. O `httpx` é async nativo e tem uma API bem parecida com o requests.

### Cache em memória
Implementei um cache simples com TTL usando um dict. Pra um case técnico funciona bem, mas em produção com múltiplas instâncias precisaria de Redis.

### Por que não usei uma lib de cache?
Quis mostrar que sei implementar a lógica, não só instalar pacotes. O cache é ~30 linhas de código e faz exatamente o que preciso.

### Rate limiting próprio
A SWAPI tem limite de 10k requisições/dia. Implementei um rate limiter usando token bucket pra não estourar o limite. É conservador (5 req/s) mas garante que não vai dar problema.

## Variáveis de ambiente

### Backend (.env)
```
API_KEY=sua-chave-secreta
SWAPI_BASE_URL=https://swapi.dev/api
LOG_LEVEL=INFO
CACHE_TTL_SECONDS=300
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_API_KEY=sua-chave-secreta
```

## TODOs

- [ ] Cache Redis para produção
- [ ] Testes de integração
- [ ] CI/CD com GitHub Actions
- [ ] Métricas e logging estruturado
- [ ] Rate limiting por API key

---

Feito para o case técnico da PowerOfData.

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.dependencies import get_swapi_client
from src.exceptions.handlers import (
    InvalidApiKeyError,
    SwapiError,
    invalid_api_key_handler,
    swapi_error_handler,
)
from src.routers import characters, films, planets, starships
from src.schemas.models import HealthResponse


settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    logger.info("Starting up PowerOfData SWAPI API...")
    yield
    # Cleanup on shutdown
    logger.info("Shutting down...")
    client = get_swapi_client()
    await client.close()
    logger.info("SWAPI client closed")


app = FastAPI(
    title=settings.api_title,
    description="""
    API para exploração do universo Star Wars, consumindo dados da SWAPI.

    ## Recursos disponíveis

    - **Characters**: Personagens do universo Star Wars
    - **Planets**: Planetas
    - **Starships**: Naves estelares
    - **Films**: Os 6 filmes clássicos

    ## Autenticação

    Todas as rotas (exceto /health) requerem uma API key no header `X-API-Key`.

    ## Consultas correlacionadas

    Cada recurso possui endpoints para buscar dados relacionados:
    - `/characters/{id}/films` - Filmes de um personagem
    - `/films/{id}/characters` - Personagens de um filme
    - `/planets/{id}/residents` - Residentes de um planeta
    - etc.
    """,
    version=settings.api_version,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware for tracing
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    # Make request_id available in request state
    request.state.request_id = request_id

    logger.debug(f"[{request_id}] {request.method} {request.url.path}")

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# Exception handlers
app.add_exception_handler(SwapiError, swapi_error_handler)
app.add_exception_handler(InvalidApiKeyError, invalid_api_key_handler)


# Generic exception handler for unexpected errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(f"[{request_id}] Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "request_id": request_id,
        },
    )


# Include routers
app.include_router(characters.router)
app.include_router(planets.router)
app.include_router(starships.router)
app.include_router(films.router)


# Health check endpoint (no auth required)
@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return HealthResponse(status="healthy", version=settings.api_version)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to docs."""
    return {"message": "Welcome to PowerOfData SWAPI API", "docs": "/docs"}

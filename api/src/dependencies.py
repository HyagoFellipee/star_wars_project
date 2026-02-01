from typing import Annotated

from fastapi import Header

from src.config import get_settings
from src.exceptions.handlers import InvalidApiKeyError
from src.services.swapi_client import SwapiClient


settings = get_settings()

# Singleton client instance - created on first use
# TODO: Consider using lifespan context manager for proper cleanup
_swapi_client: SwapiClient | None = None


def get_swapi_client() -> SwapiClient:
    """
    Get the SWAPI client singleton.

    Using a singleton here because creating httpx.AsyncClient
    for every request is wasteful - connection pooling FTW.
    """
    global _swapi_client
    if _swapi_client is None:
        _swapi_client = SwapiClient()
    return _swapi_client


async def verify_api_key(
    x_api_key: Annotated[str | None, Header()] = None
) -> str:
    """
    Validate API key from X-API-Key header.

    For now it's just a simple string comparison against env var.
    Good enough for a technical challenge, but in production we'd
    want proper key management (rotation, scoping, rate limits per key, etc).
    """
    if x_api_key is None:
        raise InvalidApiKeyError("Missing X-API-Key header")

    if x_api_key != settings.api_key:
        raise InvalidApiKeyError("Invalid API key")

    return x_api_key


# Type alias for dependency injection
ApiKeyDep = Annotated[str, verify_api_key]
SwapiClientDep = Annotated[SwapiClient, get_swapi_client]

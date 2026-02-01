from fastapi import Request
from fastapi.responses import JSONResponse


class SwapiError(Exception):
    """Base exception for SWAPI-related errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class SwapiNotFoundError(SwapiError):
    """Resource not found in SWAPI."""

    def __init__(self, resource_type: str, resource_id: int):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            message=f"{resource_type.capitalize()} with id {resource_id} not found",
            status_code=404,
        )


class SwapiTimeoutError(SwapiError):
    """SWAPI request timed out after retries."""

    def __init__(self, attempts: int):
        self.attempts = attempts
        super().__init__(
            message=f"SWAPI request timed out after {attempts} attempts",
            status_code=504,
        )


class SwapiRateLimitError(SwapiError):
    """Hit SWAPI rate limit."""

    def __init__(self):
        super().__init__(
            message="SWAPI rate limit exceeded. Please try again later.",
            status_code=429,
        )


class InvalidApiKeyError(Exception):
    """Invalid or missing API key."""

    def __init__(self, message: str = "Invalid or missing API key"):
        self.message = message
        super().__init__(self.message)


# FastAPI exception handlers


async def swapi_error_handler(request: Request, exc: SwapiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "path": str(request.url),
        },
    )


async def invalid_api_key_handler(
    request: Request, exc: InvalidApiKeyError
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={
            "error": "Unauthorized",
            "message": exc.message,
        },
    )

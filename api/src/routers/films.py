import math
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.dependencies import get_swapi_client, verify_api_key
from src.schemas.models import (
    CharacterSummary,
    Film,
    FilmSummary,
    PaginatedResponse,
    PlanetSummary,
    StarshipSummary,
)
from src.services.swapi_client import SwapiClient


router = APIRouter(
    prefix="/films",
    tags=["films"],
    dependencies=[Depends(verify_api_key)],
)


class FilmSortField(str, Enum):
    title = "title"
    episode_id = "episode_id"
    release_date = "release_date"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


def _apply_filters(
    films: list[FilmSummary],
    filters: dict[str, str | None],
) -> list[FilmSummary]:
    """Apply case-insensitive filters to film list."""
    result = films
    for field, value in filters.items():
        if value is not None:
            result = [
                film for film in result
                if value.lower() in getattr(film, field, "").lower()
            ]
    return result


def _sort_films(
    films: list[FilmSummary],
    sort_by: FilmSortField,
    order: SortOrder,
) -> list[FilmSummary]:
    """Sort film list by given field."""
    reverse = order == SortOrder.desc

    def get_sort_key(film: FilmSummary):
        value = getattr(film, sort_by.value)
        if sort_by == FilmSortField.episode_id:
            return value  # Already an int
        return value.lower() if isinstance(value, str) else value

    return sorted(films, key=get_sort_key, reverse=reverse)


PAGE_SIZE = 10


@router.get("/", response_model=PaginatedResponse[FilmSummary])
async def list_films(
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
    page: int = Query(1, ge=1, description="Page number"),
    search: str | None = Query(None, description="Search by title"),
    sort_by: FilmSortField = Query(
        FilmSortField.episode_id, description="Field to sort by"
    ),
    order: SortOrder = Query(SortOrder.asc, description="Sort order"),
    director: str | None = Query(None, description="Filter by director"),
    producer: str | None = Query(None, description="Filter by producer"),
):
    """
    List all films with pagination, search, sorting, and filters.

    Note: There are only 6 films in SWAPI. Default sort is by episode_id
    to show films in chronological order.
    """
    # Fetch ALL films (cached after first request)
    all_data = await client.fetch_all_films(search=search)

    films = []
    for item in all_data:
        film_id = client._extract_id_from_url(item["url"])
        films.append(client._parse_film_summary(item, film_id))

    # Apply filters
    filters = {"director": director, "producer": producer}
    filtered_films = _apply_filters(films, filters)

    # Sort results
    sorted_films = _sort_films(filtered_films, sort_by, order)

    # Paginate
    total_count = len(sorted_films)
    total_pages = math.ceil(total_count / PAGE_SIZE) if total_count > 0 else 1
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_results = sorted_films[start_idx:end_idx]

    return PaginatedResponse(
        count=total_count,
        page=page,
        total_pages=total_pages,
        next_page=page + 1 if page < total_pages else None,
        previous_page=page - 1 if page > 1 else None,
        results=page_results,
    )


@router.get("/{film_id}", response_model=Film)
async def get_film(
    film_id: int,
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
):
    """Get a single film by ID."""
    return await client.get_film(film_id)


@router.get("/{film_id}/characters", response_model=list[CharacterSummary])
async def get_film_characters(
    film_id: int,
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
):
    """
    Get all characters that appear in a film.

    Warning: Some films have 20+ characters, so this endpoint
    can be slow due to multiple SWAPI requests.
    """
    return await client.get_film_characters(film_id)


@router.get("/{film_id}/planets", response_model=list[PlanetSummary])
async def get_film_planets(
    film_id: int,
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
):
    """Get all planets featured in a film."""
    return await client.get_film_planets(film_id)


@router.get("/{film_id}/starships", response_model=list[StarshipSummary])
async def get_film_starships(
    film_id: int,
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
):
    """Get all starships that appear in a film."""
    return await client.get_film_starships(film_id)

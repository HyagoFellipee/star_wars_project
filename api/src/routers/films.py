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


@router.get("/", response_model=PaginatedResponse[FilmSummary])
async def list_films(
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
    page: int = Query(1, ge=1, description="Page number"),
    search: str | None = Query(None, description="Search by title"),
    sort_by: FilmSortField = Query(
        FilmSortField.episode_id, description="Field to sort by"
    ),
    order: SortOrder = Query(SortOrder.asc, description="Sort order"),
):
    """
    List all films with pagination, search, and sorting.

    Note: There are only 6 films in SWAPI, so pagination is mostly
    for API consistency. Default sort is by episode_id to show
    films in chronological order.
    """
    data = await client.fetch_films(page=page, search=search)

    films = []
    for item in data.get("results", []):
        film_id = client._extract_id_from_url(item["url"])
        films.append(client._parse_film_summary(item, film_id))

    sorted_films = _sort_films(films, sort_by, order)

    total_count = data.get("count", 0)
    total_pages = math.ceil(total_count / 10) if total_count > 0 else 1

    return PaginatedResponse(
        count=total_count,
        page=page,
        total_pages=total_pages,
        next_page=page + 1 if data.get("next") else None,
        previous_page=page - 1 if data.get("previous") else None,
        results=sorted_films,
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

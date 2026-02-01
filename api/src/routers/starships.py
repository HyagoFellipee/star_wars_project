import math
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.dependencies import get_swapi_client, verify_api_key
from src.schemas.models import (
    CharacterSummary,
    FilmSummary,
    PaginatedResponse,
    Starship,
    StarshipSummary,
)
from src.services.swapi_client import SwapiClient


router = APIRouter(
    prefix="/starships",
    tags=["starships"],
    dependencies=[Depends(verify_api_key)],
)


class StarshipSortField(str, Enum):
    name = "name"
    model = "model"
    starship_class = "starship_class"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


def _sort_starships(
    starships: list[StarshipSummary],
    sort_by: StarshipSortField,
    order: SortOrder,
) -> list[StarshipSummary]:
    """Sort starship list by given field."""
    reverse = order == SortOrder.desc

    def get_sort_key(ship: StarshipSummary):
        value = getattr(ship, sort_by.value)
        return value.lower() if isinstance(value, str) else value

    return sorted(starships, key=get_sort_key, reverse=reverse)


@router.get("/", response_model=PaginatedResponse[StarshipSummary])
async def list_starships(
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
    page: int = Query(1, ge=1, description="Page number"),
    search: str | None = Query(None, description="Search by name or model"),
    sort_by: StarshipSortField = Query(
        StarshipSortField.name, description="Field to sort by"
    ),
    order: SortOrder = Query(SortOrder.asc, description="Sort order"),
):
    """List all starships with pagination, search, and sorting."""
    data = await client.fetch_starships(page=page, search=search)

    starships = []
    for item in data.get("results", []):
        ship_id = client._extract_id_from_url(item["url"])
        starships.append(client._parse_starship_summary(item, ship_id))

    sorted_ships = _sort_starships(starships, sort_by, order)

    total_count = data.get("count", 0)
    total_pages = math.ceil(total_count / 10) if total_count > 0 else 1

    return PaginatedResponse(
        count=total_count,
        page=page,
        total_pages=total_pages,
        next_page=page + 1 if data.get("next") else None,
        previous_page=page - 1 if data.get("previous") else None,
        results=sorted_ships,
    )


@router.get("/{starship_id}", response_model=Starship)
async def get_starship(
    starship_id: int,
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
):
    """Get a single starship by ID."""
    return await client.get_starship(starship_id)


@router.get("/{starship_id}/pilots", response_model=list[CharacterSummary])
async def get_starship_pilots(
    starship_id: int,
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
):
    """
    Get all pilots of a starship.

    Note: Many starships in SWAPI have no pilots listed,
    so this often returns an empty list.
    """
    return await client.get_starship_pilots(starship_id)


@router.get("/{starship_id}/films", response_model=list[FilmSummary])
async def get_starship_films(
    starship_id: int,
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
):
    """Get all films that a starship appears in."""
    starship = await client.get_starship(starship_id)
    films = []
    for url in starship.film_urls:
        film_id = client._extract_id_from_url(url)
        film_data = await client.fetch_film(film_id)
        films.append(client._parse_film_summary(film_data, film_id))
    return films

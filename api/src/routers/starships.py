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


def _apply_filters(
    starships: list[StarshipSummary],
    filters: dict[str, str | None],
) -> list[StarshipSummary]:
    """Apply case-insensitive filters to starship list."""
    result = starships
    for field, value in filters.items():
        if value is not None:
            result = [
                ship for ship in result
                if value.lower() in getattr(ship, field, "").lower()
            ]
    return result


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


PAGE_SIZE = 10


@router.get("/", response_model=PaginatedResponse[StarshipSummary])
async def list_starships(
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
    page: int = Query(1, ge=1, description="Page number"),
    search: str | None = Query(None, description="Search by name or model"),
    sort_by: StarshipSortField = Query(
        StarshipSortField.name, description="Field to sort by"
    ),
    order: SortOrder = Query(SortOrder.asc, description="Sort order"),
    starship_class: str | None = Query(None, description="Filter by starship class"),
    manufacturer: str | None = Query(None, description="Filter by manufacturer"),
    film_id: int | None = Query(None, description="Filter by film ID (starships in film)"),
):
    """
    List all starships with pagination, search, sorting, and filters.

    Fetches all data from SWAPI, applies filters/sorting, then paginates.
    """
    # Fetch ALL starships (cached after first request)
    all_data = await client.fetch_all_starships(search=search)

    # If filtering by film, get the film's starship URLs
    film_ship_urls: set[str] | None = None
    if film_id:
        film_data = await client.fetch_film(film_id)
        film_ship_urls = set(film_data.get("starships", []))

    starships = []
    for item in all_data:
        # Filter by film if specified
        if film_ship_urls is not None and item["url"] not in film_ship_urls:
            continue
        ship_id = client._extract_id_from_url(item["url"])
        starships.append(client._parse_starship_summary(item, ship_id))

    # Apply filters
    filters = {"starship_class": starship_class, "manufacturer": manufacturer}
    filtered_ships = _apply_filters(starships, filters)

    # Sort results
    sorted_ships = _sort_starships(filtered_ships, sort_by, order)

    # Paginate
    total_count = len(sorted_ships)
    total_pages = math.ceil(total_count / PAGE_SIZE) if total_count > 0 else 1
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_results = sorted_ships[start_idx:end_idx]

    return PaginatedResponse(
        count=total_count,
        page=page,
        total_pages=total_pages,
        next_page=page + 1 if page < total_pages else None,
        previous_page=page - 1 if page > 1 else None,
        results=page_results,
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

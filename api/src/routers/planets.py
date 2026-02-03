import math
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.dependencies import get_swapi_client, verify_api_key
from src.schemas.models import (
    CharacterSummary,
    FilmSummary,
    PaginatedResponse,
    Planet,
    PlanetSummary,
)
from src.services.swapi_client import SwapiClient


router = APIRouter(
    prefix="/planets",
    tags=["planets"],
    dependencies=[Depends(verify_api_key)],
)


class PlanetSortField(str, Enum):
    name = "name"
    population = "population"
    diameter = "diameter"
    climate = "climate"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


def _apply_filters(
    planets: list[PlanetSummary],
    filters: dict[str, str | None],
) -> list[PlanetSummary]:
    """Apply case-insensitive filters to planet list."""
    result = planets
    for field, value in filters.items():
        if value is not None:
            result = [
                planet for planet in result
                if value.lower() in getattr(planet, field, "").lower()
            ]
    return result


def _sort_planets(
    planets: list[PlanetSummary],
    sort_by: PlanetSortField,
    order: SortOrder,
) -> list[PlanetSummary]:
    """Sort planet list by given field."""
    reverse = order == SortOrder.desc

    def get_sort_key(planet: PlanetSummary):
        value = getattr(planet, sort_by.value)
        if sort_by in (PlanetSortField.population, PlanetSortField.diameter):
            try:
                return float(value.replace(",", ""))
            except (ValueError, AttributeError):
                return float("inf") if not reverse else float("-inf")
        return value.lower() if isinstance(value, str) else value

    return sorted(planets, key=get_sort_key, reverse=reverse)


PAGE_SIZE = 10


@router.get("/", response_model=PaginatedResponse[PlanetSummary])
async def list_planets(
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
    page: int = Query(1, ge=1, description="Page number"),
    search: str | None = Query(None, description="Search by name"),
    sort_by: PlanetSortField = Query(
        PlanetSortField.name, description="Field to sort by"
    ),
    order: SortOrder = Query(SortOrder.asc, description="Sort order"),
    climate: str | None = Query(None, description="Filter by climate (arid, temperate, etc.)"),
    terrain: str | None = Query(None, description="Filter by terrain (desert, grasslands, etc.)"),
    film_id: int | None = Query(None, description="Filter by film ID (planets in film)"),
):
    """
    List all planets with pagination, search, sorting, and filters.

    Fetches all data from SWAPI, applies filters/sorting, then paginates.
    """
    # Fetch ALL planets (cached after first request)
    all_data = await client.fetch_all_planets(search=search)

    # If filtering by film, get the film's planet URLs
    film_planet_urls: set[str] | None = None
    if film_id:
        film_data = await client.fetch_film(film_id)
        film_planet_urls = set(film_data.get("planets", []))

    planets = []
    for item in all_data:
        # Filter by film if specified
        if film_planet_urls is not None and item["url"] not in film_planet_urls:
            continue
        planet_id = client._extract_id_from_url(item["url"])
        planets.append(client._parse_planet_summary(item, planet_id))

    # Apply filters
    filters = {"climate": climate, "terrain": terrain}
    filtered_planets = _apply_filters(planets, filters)

    # Sort results
    sorted_planets = _sort_planets(filtered_planets, sort_by, order)

    # Paginate
    total_count = len(sorted_planets)
    total_pages = math.ceil(total_count / PAGE_SIZE) if total_count > 0 else 1
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_results = sorted_planets[start_idx:end_idx]

    return PaginatedResponse(
        count=total_count,
        page=page,
        total_pages=total_pages,
        next_page=page + 1 if page < total_pages else None,
        previous_page=page - 1 if page > 1 else None,
        results=page_results,
    )


@router.get("/{planet_id}", response_model=Planet)
async def get_planet(
    planet_id: int,
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
):
    """Get a single planet by ID."""
    return await client.get_planet(planet_id)


@router.get("/{planet_id}/residents", response_model=list[CharacterSummary])
async def get_planet_residents(
    planet_id: int,
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
):
    """Get all residents of a planet."""
    return await client.get_planet_residents(planet_id)


@router.get("/{planet_id}/films", response_model=list[FilmSummary])
async def get_planet_films(
    planet_id: int,
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
):
    """Get all films that feature a planet."""
    planet = await client.get_planet(planet_id)
    films = []
    for url in planet.film_urls:
        film_id = client._extract_id_from_url(url)
        film_data = await client.fetch_film(film_id)
        films.append(client._parse_film_summary(film_data, film_id))
    return films

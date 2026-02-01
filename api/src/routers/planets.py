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


@router.get("/", response_model=PaginatedResponse[PlanetSummary])
async def list_planets(
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
    page: int = Query(1, ge=1, description="Page number"),
    search: str | None = Query(None, description="Search by name"),
    sort_by: PlanetSortField = Query(
        PlanetSortField.name, description="Field to sort by"
    ),
    order: SortOrder = Query(SortOrder.asc, description="Sort order"),
):
    """List all planets with pagination, search, and sorting."""
    data = await client.fetch_planets(page=page, search=search)

    planets = []
    for item in data.get("results", []):
        planet_id = client._extract_id_from_url(item["url"])
        planets.append(client._parse_planet_summary(item, planet_id))

    sorted_planets = _sort_planets(planets, sort_by, order)

    total_count = data.get("count", 0)
    total_pages = math.ceil(total_count / 10) if total_count > 0 else 1

    return PaginatedResponse(
        count=total_count,
        page=page,
        total_pages=total_pages,
        next_page=page + 1 if data.get("next") else None,
        previous_page=page - 1 if data.get("previous") else None,
        results=sorted_planets,
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

import math
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.dependencies import get_swapi_client, verify_api_key
from src.schemas.models import (
    Character,
    CharacterSummary,
    FilmSummary,
    PaginatedResponse,
)
from src.services.swapi_client import SwapiClient


router = APIRouter(
    prefix="/characters",
    tags=["characters"],
    dependencies=[Depends(verify_api_key)],
)


class CharacterSortField(str, Enum):
    name = "name"
    height = "height"
    mass = "mass"
    birth_year = "birth_year"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


def _sort_characters(
    characters: list[CharacterSummary],
    sort_by: CharacterSortField,
    order: SortOrder,
) -> list[CharacterSummary]:
    """Sort character list by given field and order."""
    reverse = order == SortOrder.desc

    def get_sort_key(char: CharacterSummary):
        value = getattr(char, sort_by.value)
        # Handle "unknown" and numeric strings
        if sort_by in (CharacterSortField.height, CharacterSortField.mass):
            try:
                return float(value.replace(",", ""))
            except (ValueError, AttributeError):
                # Push "unknown" to the end
                return float("inf") if not reverse else float("-inf")
        return value.lower() if isinstance(value, str) else value

    return sorted(characters, key=get_sort_key, reverse=reverse)


@router.get("/", response_model=PaginatedResponse[CharacterSummary])
async def list_characters(
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
    page: int = Query(1, ge=1, description="Page number"),
    search: str | None = Query(None, description="Search by name"),
    sort_by: CharacterSortField = Query(
        CharacterSortField.name, description="Field to sort by"
    ),
    order: SortOrder = Query(SortOrder.asc, description="Sort order"),
):
    """
    List all characters with pagination, search, and sorting.

    The SWAPI returns 10 items per page. We pass through their pagination
    and add sorting on our end (since SWAPI doesn't support it).
    """
    data = await client.fetch_people(page=page, search=search)

    # Parse results into summaries
    characters = []
    for item in data.get("results", []):
        char_id = client._extract_id_from_url(item["url"])
        characters.append(client._parse_character_summary(item, char_id))

    # Sort results
    sorted_chars = _sort_characters(characters, sort_by, order)

    total_count = data.get("count", 0)
    total_pages = math.ceil(total_count / 10) if total_count > 0 else 1

    return PaginatedResponse(
        count=total_count,
        page=page,
        total_pages=total_pages,
        next_page=page + 1 if data.get("next") else None,
        previous_page=page - 1 if data.get("previous") else None,
        results=sorted_chars,
    )


@router.get("/{character_id}", response_model=Character)
async def get_character(
    character_id: int,
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
    include_homeworld: bool = Query(
        False, description="Include homeworld planet details"
    ),
):
    """Get a single character by ID, optionally with homeworld data."""
    if include_homeworld:
        return await client.get_character_with_homeworld(character_id)
    return await client.get_character(character_id)


@router.get("/{character_id}/films", response_model=list[FilmSummary])
async def get_character_films(
    character_id: int,
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
):
    """Get all films that a character appears in."""
    return await client.get_character_films(character_id)

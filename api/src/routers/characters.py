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


def _apply_filters(
    characters: list[CharacterSummary],
    filters: dict[str, str | None],
    exact_match_fields: set[str] | None = None,
) -> list[CharacterSummary]:
    """Apply case-insensitive filters to character list.

    Args:
        exact_match_fields: Fields that require exact match (e.g., 'gender')
                           instead of substring match.
    """
    exact_fields = exact_match_fields or set()
    result = characters
    for field, value in filters.items():
        if value is not None:
            if field in exact_fields:
                result = [
                    char for char in result
                    if getattr(char, field, "").lower() == value.lower()
                ]
            else:
                result = [
                    char for char in result
                    if value.lower() in getattr(char, field, "").lower()
                ]
    return result


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


PAGE_SIZE = 10


@router.get("/", response_model=PaginatedResponse[CharacterSummary])
async def list_characters(
    client: Annotated[SwapiClient, Depends(get_swapi_client)],
    page: int = Query(1, ge=1, description="Page number"),
    search: str | None = Query(None, description="Search by name"),
    sort_by: CharacterSortField = Query(
        CharacterSortField.name, description="Field to sort by"
    ),
    order: SortOrder = Query(SortOrder.asc, description="Sort order"),
    gender: str | None = Query(None, description="Filter by gender (male, female, n/a)"),
    eye_color: str | None = Query(None, description="Filter by eye color"),
    hair_color: str | None = Query(None, description="Filter by hair color"),
    skin_color: str | None = Query(None, description="Filter by skin color"),
    film_id: int | None = Query(None, description="Filter by film ID (characters in film)"),
):
    """
    List all characters with pagination, search, sorting, and filters.

    Fetches all data from SWAPI, applies filters/sorting, then paginates.
    Results are cached to improve performance on subsequent requests.
    """
    # Fetch ALL characters (cached after first request)
    all_data = await client.fetch_all_people(search=search)

    # If filtering by film, get the film's character URLs
    film_char_urls: set[str] | None = None
    if film_id:
        film_data = await client.fetch_film(film_id)
        film_char_urls = set(film_data.get("characters", []))

    # Parse results into summaries
    characters = []
    for item in all_data:
        # Filter by film if specified
        if film_char_urls is not None and item["url"] not in film_char_urls:
            continue
        char_id = client._extract_id_from_url(item["url"])
        characters.append(client._parse_character_summary(item, char_id))

    # Apply filters
    filters = {
        "gender": gender,
        "eye_color": eye_color,
        "hair_color": hair_color,
        "skin_color": skin_color,
    }
    filtered_chars = _apply_filters(characters, filters, exact_match_fields={"gender"})

    # Sort results
    sorted_chars = _sort_characters(filtered_chars, sort_by, order)

    # Paginate
    total_count = len(sorted_chars)
    total_pages = math.ceil(total_count / PAGE_SIZE) if total_count > 0 else 1
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_results = sorted_chars[start_idx:end_idx]

    return PaginatedResponse(
        count=total_count,
        page=page,
        total_pages=total_pages,
        next_page=page + 1 if page < total_pages else None,
        previous_page=page - 1 if page > 1 else None,
        results=page_results,
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

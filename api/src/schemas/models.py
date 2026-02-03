from typing import Generic, TypeVar

from pydantic import BaseModel, Field, ConfigDict


T = TypeVar("T")


# --- Base models for SWAPI resources ---


class CharacterBase(BaseModel):
    """Base character data from SWAPI (people endpoint)."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    height: str  # SWAPI returns strings, even for numbers
    mass: str
    hair_color: str
    skin_color: str
    eye_color: str
    birth_year: str
    gender: str
    homeworld_url: str = Field(alias="homeworld")

    # These are URLs in SWAPI responses
    film_urls: list[str] = Field(default_factory=list, alias="films")
    species_urls: list[str] = Field(default_factory=list, alias="species")
    vehicle_urls: list[str] = Field(default_factory=list, alias="vehicles")
    starship_urls: list[str] = Field(default_factory=list, alias="starships")


class Character(CharacterBase):
    """Character with optionally enriched data."""

    # Enriched fields - populated when requested
    homeworld: "Planet | None" = None
    films_data: list["FilmSummary"] = Field(default_factory=list)


class CharacterSummary(BaseModel):
    """Lightweight character for lists and references."""

    id: int
    name: str
    gender: str
    birth_year: str
    eye_color: str = ""
    hair_color: str = ""
    skin_color: str = ""


class PlanetBase(BaseModel):
    """Base planet data from SWAPI."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    rotation_period: str
    orbital_period: str
    diameter: str
    climate: str
    gravity: str
    terrain: str
    surface_water: str
    population: str

    resident_urls: list[str] = Field(default_factory=list, alias="residents")
    film_urls: list[str] = Field(default_factory=list, alias="films")


class Planet(PlanetBase):
    """Planet with optionally enriched data."""

    residents_data: list[CharacterSummary] = Field(default_factory=list)
    films_data: list["FilmSummary"] = Field(default_factory=list)


class PlanetSummary(BaseModel):
    """Lightweight planet for references."""

    id: int
    name: str
    climate: str
    terrain: str


class StarshipBase(BaseModel):
    """Base starship data from SWAPI."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    model: str
    manufacturer: str
    cost_in_credits: str
    length: str
    max_atmosphering_speed: str
    crew: str
    passengers: str
    cargo_capacity: str
    consumables: str
    hyperdrive_rating: str
    MGLT: str  # Megalights per hour
    starship_class: str

    pilot_urls: list[str] = Field(default_factory=list, alias="pilots")
    film_urls: list[str] = Field(default_factory=list, alias="films")


class Starship(StarshipBase):
    """Starship with optionally enriched data."""

    pilots_data: list[CharacterSummary] = Field(default_factory=list)
    films_data: list["FilmSummary"] = Field(default_factory=list)


class StarshipSummary(BaseModel):
    """Lightweight starship for references."""

    id: int
    name: str
    model: str
    starship_class: str
    manufacturer: str = ""


class FilmBase(BaseModel):
    """Base film data from SWAPI."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    title: str
    episode_id: int
    opening_crawl: str
    director: str
    producer: str
    release_date: str

    character_urls: list[str] = Field(default_factory=list, alias="characters")
    planet_urls: list[str] = Field(default_factory=list, alias="planets")
    starship_urls: list[str] = Field(default_factory=list, alias="starships")
    vehicle_urls: list[str] = Field(default_factory=list, alias="vehicles")
    species_urls: list[str] = Field(default_factory=list, alias="species")


class Film(FilmBase):
    """Film with optionally enriched data."""

    characters_data: list[CharacterSummary] = Field(default_factory=list)
    planets_data: list[PlanetSummary] = Field(default_factory=list)
    starships_data: list[StarshipSummary] = Field(default_factory=list)


class FilmSummary(BaseModel):
    """Lightweight film for references."""

    id: int
    title: str
    episode_id: int
    release_date: str
    director: str = ""
    producer: str = ""


# --- Response wrappers ---


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper."""

    count: int  # Total items across all pages
    page: int
    total_pages: int
    next_page: int | None = None
    previous_page: int | None = None
    results: list[T]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


# Forward refs for self-referencing models
Character.model_rebuild()
Planet.model_rebuild()

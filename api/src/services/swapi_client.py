import asyncio
import logging
import re
import time
from typing import Any

import httpx

from src.config import get_settings
from src.exceptions.handlers import (
    SwapiNotFoundError,
    SwapiRateLimitError,
    SwapiTimeoutError,
)
from src.schemas.models import (
    Character,
    CharacterSummary,
    Film,
    FilmSummary,
    Planet,
    PlanetSummary,
    Starship,
    StarshipSummary,
)


logger = logging.getLogger(__name__)
settings = get_settings()


class SimpleCache:
    """
    Dead simple in-memory cache with TTL.

    TODO: Replace with Redis for production - this won't work
    with multiple Cloud Run instances sharing state.
    """

    def __init__(self, ttl_seconds: int = 300):
        self._cache: dict[str, tuple[Any, float]] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Any | None:
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        if time.time() - timestamp > self._ttl:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        self._cache.clear()


class RateLimiter:
    """Simple token bucket rate limiter."""

    def __init__(self, requests_per_second: float):
        self._rate = requests_per_second
        self._tokens = requests_per_second
        self._last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.time()
            elapsed = now - self._last_update
            self._tokens = min(self._rate, self._tokens + elapsed * self._rate)
            self._last_update = now

            if self._tokens < 1:
                wait_time = (1 - self._tokens) / self._rate
                logger.debug(f"Rate limited, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                self._tokens = 0
            else:
                self._tokens -= 1


class SwapiClient:
    """
    Async client for the Star Wars API (swapi.dev).

    Features:
    - In-memory caching with TTL
    - Rate limiting to avoid hitting SWAPI limits
    - Automatic retry with exponential backoff
    - Data enrichment for correlated queries
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        cache_ttl: int | None = None,
    ):
        self._base_url = base_url or settings.swapi_base_url
        self._timeout = timeout or settings.swapi_timeout
        self._max_retries = settings.swapi_max_retries

        self._cache = SimpleCache(ttl_seconds=cache_ttl or settings.cache_ttl_seconds)
        self._rate_limiter = RateLimiter(settings.rate_limit_requests_per_second)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _extract_id_from_url(self, url: str) -> int:
        """Extract resource ID from SWAPI URL like https://swapi.dev/api/people/1/"""
        match = re.search(r"/(\d+)/?$", url)
        if not match:
            raise ValueError(f"Could not extract ID from URL: {url}")
        return int(match.group(1))

    async def _fetch_with_retry(self, endpoint: str) -> dict[str, Any]:
        """Fetch from SWAPI with caching, rate limiting, and retry logic."""
        cache_key = endpoint
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit for {endpoint}")
            return cached

        client = await self._get_client()
        last_error: Exception | None = None

        for attempt in range(1, self._max_retries + 1):
            try:
                await self._rate_limiter.acquire()
                logger.debug(f"Fetching {endpoint} (attempt {attempt})")

                response = await client.get(endpoint)

                if response.status_code == 404:
                    raise SwapiNotFoundError("resource", 0)  # ID filled by caller
                if response.status_code == 429:
                    raise SwapiRateLimitError()

                response.raise_for_status()
                data = response.json()
                self._cache.set(cache_key, data)
                return data

            except httpx.TimeoutException as e:
                last_error = e
                if attempt < self._max_retries:
                    backoff = 2 ** (attempt - 1)  # 1, 2, 4 seconds
                    logger.warning(
                        f"Timeout on {endpoint}, retrying in {backoff}s "
                        f"(attempt {attempt}/{self._max_retries})"
                    )
                    await asyncio.sleep(backoff)
            except SwapiRateLimitError:
                raise
            except SwapiNotFoundError:
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching {endpoint}: {e}")
                raise

        raise SwapiTimeoutError(attempts=self._max_retries)

    # --- Core fetch methods ---

    async def fetch_people(
        self, page: int = 1, search: str | None = None
    ) -> dict[str, Any]:
        """Fetch paginated list of people/characters."""
        endpoint = f"/people/?page={page}"
        if search:
            endpoint += f"&search={search}"
        return await self._fetch_with_retry(endpoint)

    async def fetch_person(self, person_id: int) -> dict[str, Any]:
        """Fetch a single person by ID."""
        try:
            return await self._fetch_with_retry(f"/people/{person_id}/")
        except SwapiNotFoundError:
            raise SwapiNotFoundError("character", person_id)

    async def fetch_planets(
        self, page: int = 1, search: str | None = None
    ) -> dict[str, Any]:
        endpoint = f"/planets/?page={page}"
        if search:
            endpoint += f"&search={search}"
        return await self._fetch_with_retry(endpoint)

    async def fetch_planet(self, planet_id: int) -> dict[str, Any]:
        try:
            return await self._fetch_with_retry(f"/planets/{planet_id}/")
        except SwapiNotFoundError:
            raise SwapiNotFoundError("planet", planet_id)

    async def fetch_starships(
        self, page: int = 1, search: str | None = None
    ) -> dict[str, Any]:
        endpoint = f"/starships/?page={page}"
        if search:
            endpoint += f"&search={search}"
        return await self._fetch_with_retry(endpoint)

    async def fetch_starship(self, starship_id: int) -> dict[str, Any]:
        try:
            return await self._fetch_with_retry(f"/starships/{starship_id}/")
        except SwapiNotFoundError:
            raise SwapiNotFoundError("starship", starship_id)

    async def fetch_films(
        self, page: int = 1, search: str | None = None
    ) -> dict[str, Any]:
        endpoint = f"/films/?page={page}"
        if search:
            endpoint += f"&search={search}"
        return await self._fetch_with_retry(endpoint)

    async def fetch_film(self, film_id: int) -> dict[str, Any]:
        try:
            return await self._fetch_with_retry(f"/films/{film_id}/")
        except SwapiNotFoundError:
            raise SwapiNotFoundError("film", film_id)

    # --- Fetch ALL data methods (for proper filtering/pagination) ---

    async def fetch_all_people(self, search: str | None = None) -> list[dict[str, Any]]:
        """Fetch ALL people from SWAPI (all pages)."""
        cache_key = f"all_people:{search or ''}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # First request to get total count
        first_page = await self.fetch_people(page=1, search=search)
        total_count = first_page.get("count", 0)
        all_results = list(first_page.get("results", []))

        if total_count > 10:
            # Fetch remaining pages in parallel
            total_pages = (total_count + 9) // 10
            tasks = [
                self.fetch_people(page=p, search=search)
                for p in range(2, total_pages + 1)
            ]
            pages = await asyncio.gather(*tasks)
            for page_data in pages:
                all_results.extend(page_data.get("results", []))

        self._cache.set(cache_key, all_results)
        return all_results

    async def fetch_all_planets(self, search: str | None = None) -> list[dict[str, Any]]:
        """Fetch ALL planets from SWAPI (all pages)."""
        cache_key = f"all_planets:{search or ''}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        first_page = await self.fetch_planets(page=1, search=search)
        total_count = first_page.get("count", 0)
        all_results = list(first_page.get("results", []))

        if total_count > 10:
            total_pages = (total_count + 9) // 10
            tasks = [
                self.fetch_planets(page=p, search=search)
                for p in range(2, total_pages + 1)
            ]
            pages = await asyncio.gather(*tasks)
            for page_data in pages:
                all_results.extend(page_data.get("results", []))

        self._cache.set(cache_key, all_results)
        return all_results

    async def fetch_all_starships(self, search: str | None = None) -> list[dict[str, Any]]:
        """Fetch ALL starships from SWAPI (all pages)."""
        cache_key = f"all_starships:{search or ''}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        first_page = await self.fetch_starships(page=1, search=search)
        total_count = first_page.get("count", 0)
        all_results = list(first_page.get("results", []))

        if total_count > 10:
            total_pages = (total_count + 9) // 10
            tasks = [
                self.fetch_starships(page=p, search=search)
                for p in range(2, total_pages + 1)
            ]
            pages = await asyncio.gather(*tasks)
            for page_data in pages:
                all_results.extend(page_data.get("results", []))

        self._cache.set(cache_key, all_results)
        return all_results

    async def fetch_all_films(self, search: str | None = None) -> list[dict[str, Any]]:
        """Fetch ALL films from SWAPI (only 6 films, single page)."""
        cache_key = f"all_films:{search or ''}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        data = await self.fetch_films(page=1, search=search)
        all_results = list(data.get("results", []))
        self._cache.set(cache_key, all_results)
        return all_results

    # --- Parse raw SWAPI data into our models ---

    def _parse_character(self, data: dict[str, Any], char_id: int) -> Character:
        """Parse raw SWAPI person data into Character model."""
        return Character(
            id=char_id,
            name=data["name"],
            height=data["height"],
            mass=data["mass"],
            hair_color=data["hair_color"],
            skin_color=data["skin_color"],
            eye_color=data["eye_color"],
            birth_year=data["birth_year"],
            gender=data["gender"],
            homeworld_url=data["homeworld"],
            film_urls=data.get("films", []),
            species_urls=data.get("species", []),
            vehicle_urls=data.get("vehicles", []),
            starship_urls=data.get("starships", []),
        )

    def _parse_character_summary(
        self, data: dict[str, Any], char_id: int
    ) -> CharacterSummary:
        return CharacterSummary(
            id=char_id,
            name=data["name"],
            gender=data["gender"],
            birth_year=data["birth_year"],
            eye_color=data.get("eye_color", ""),
            hair_color=data.get("hair_color", ""),
            skin_color=data.get("skin_color", ""),
        )

    def _parse_planet(self, data: dict[str, Any], planet_id: int) -> Planet:
        return Planet(
            id=planet_id,
            name=data["name"],
            rotation_period=data["rotation_period"],
            orbital_period=data["orbital_period"],
            diameter=data["diameter"],
            climate=data["climate"],
            gravity=data["gravity"],
            terrain=data["terrain"],
            surface_water=data["surface_water"],
            population=data["population"],
            residents=data.get("residents", []),
            films=data.get("films", []),
        )

    def _parse_planet_summary(
        self, data: dict[str, Any], planet_id: int
    ) -> PlanetSummary:
        return PlanetSummary(
            id=planet_id,
            name=data["name"],
            climate=data["climate"],
            terrain=data["terrain"],
        )

    def _parse_starship(self, data: dict[str, Any], ship_id: int) -> Starship:
        return Starship(
            id=ship_id,
            name=data["name"],
            model=data["model"],
            manufacturer=data["manufacturer"],
            cost_in_credits=data["cost_in_credits"],
            length=data["length"],
            max_atmosphering_speed=data["max_atmosphering_speed"],
            crew=data["crew"],
            passengers=data["passengers"],
            cargo_capacity=data["cargo_capacity"],
            consumables=data["consumables"],
            hyperdrive_rating=data["hyperdrive_rating"],
            MGLT=data["MGLT"],
            starship_class=data["starship_class"],
            pilots=data.get("pilots", []),
            films=data.get("films", []),
        )

    def _parse_starship_summary(
        self, data: dict[str, Any], ship_id: int
    ) -> StarshipSummary:
        return StarshipSummary(
            id=ship_id,
            name=data["name"],
            model=data["model"],
            starship_class=data["starship_class"],
            manufacturer=data.get("manufacturer", ""),
        )

    def _parse_film(self, data: dict[str, Any], film_id: int) -> Film:
        return Film(
            id=film_id,
            title=data["title"],
            episode_id=data["episode_id"],
            opening_crawl=data["opening_crawl"],
            director=data["director"],
            producer=data["producer"],
            release_date=data["release_date"],
            characters=data.get("characters", []),
            planets=data.get("planets", []),
            starships=data.get("starships", []),
            vehicles=data.get("vehicles", []),
            species=data.get("species", []),
        )

    def _parse_film_summary(self, data: dict[str, Any], film_id: int) -> FilmSummary:
        return FilmSummary(
            id=film_id,
            title=data["title"],
            episode_id=data["episode_id"],
            release_date=data["release_date"],
            director=data.get("director", ""),
            producer=data.get("producer", ""),
        )

    # --- High-level methods that return parsed models ---

    async def get_character(self, character_id: int) -> Character:
        """Get a character by ID."""
        data = await self.fetch_person(character_id)
        return self._parse_character(data, character_id)

    async def get_character_with_homeworld(self, character_id: int) -> Character:
        """Get a character with their homeworld data populated."""
        char_data = await self.fetch_person(character_id)
        character = self._parse_character(char_data, character_id)

        # Fetch homeworld
        homeworld_id = self._extract_id_from_url(character.homeworld_url)
        planet_data = await self.fetch_planet(homeworld_id)
        character.homeworld = self._parse_planet(planet_data, homeworld_id)

        return character

    async def get_planet(self, planet_id: int) -> Planet:
        data = await self.fetch_planet(planet_id)
        return self._parse_planet(data, planet_id)

    async def get_starship(self, starship_id: int) -> Starship:
        data = await self.fetch_starship(starship_id)
        return self._parse_starship(data, starship_id)

    async def get_film(self, film_id: int) -> Film:
        data = await self.fetch_film(film_id)
        return self._parse_film(data, film_id)

    # --- Correlated queries ---

    async def get_character_films(self, character_id: int) -> list[FilmSummary]:
        """Get all films a character appears in."""
        char_data = await self.fetch_person(character_id)
        film_urls = char_data.get("films", [])

        films = []
        for url in film_urls:
            film_id = self._extract_id_from_url(url)
            film_data = await self.fetch_film(film_id)
            films.append(self._parse_film_summary(film_data, film_id))

        return films

    async def get_film_characters(self, film_id: int) -> list[CharacterSummary]:
        """Get all characters in a film."""
        film_data = await self.fetch_film(film_id)
        char_urls = film_data.get("characters", [])

        characters = []
        # NOTE: SWAPI returns all character URLs, could be 20+ for some films
        # Consider adding a limit parameter if performance becomes an issue
        for url in char_urls:
            char_id = self._extract_id_from_url(url)
            char_data = await self.fetch_person(char_id)
            characters.append(self._parse_character_summary(char_data, char_id))

        return characters

    async def get_film_starships(self, film_id: int) -> list[StarshipSummary]:
        """Get all starships in a film."""
        film_data = await self.fetch_film(film_id)
        ship_urls = film_data.get("starships", [])

        starships = []
        for url in ship_urls:
            ship_id = self._extract_id_from_url(url)
            ship_data = await self.fetch_starship(ship_id)
            starships.append(self._parse_starship_summary(ship_data, ship_id))

        return starships

    async def get_film_planets(self, film_id: int) -> list[PlanetSummary]:
        """Get all planets in a film."""
        film_data = await self.fetch_film(film_id)
        planet_urls = film_data.get("planets", [])

        planets = []
        for url in planet_urls:
            planet_id = self._extract_id_from_url(url)
            planet_data = await self.fetch_planet(planet_id)
            planets.append(self._parse_planet_summary(planet_data, planet_id))

        return planets

    async def get_planet_residents(self, planet_id: int) -> list[CharacterSummary]:
        """Get all residents of a planet."""
        planet_data = await self.fetch_planet(planet_id)
        resident_urls = planet_data.get("residents", [])

        residents = []
        for url in resident_urls:
            char_id = self._extract_id_from_url(url)
            char_data = await self.fetch_person(char_id)
            residents.append(self._parse_character_summary(char_data, char_id))

        return residents

    async def get_starship_pilots(self, starship_id: int) -> list[CharacterSummary]:
        """Get all pilots of a starship."""
        ship_data = await self.fetch_starship(starship_id)
        pilot_urls = ship_data.get("pilots", [])

        # FIXME: Most starships have no pilots listed in SWAPI, returns empty
        pilots = []
        for url in pilot_urls:
            char_id = self._extract_id_from_url(url)
            char_data = await self.fetch_person(char_id)
            pilots.append(self._parse_character_summary(char_data, char_id))

        return pilots

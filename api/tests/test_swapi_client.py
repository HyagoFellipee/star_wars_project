import pytest
import respx
from httpx import Response

from src.exceptions.handlers import SwapiNotFoundError, SwapiTimeoutError
from src.services.swapi_client import SwapiClient, SimpleCache


# --- SimpleCache tests ---


class TestSimpleCache:
    def test_cache_set_and_get(self):
        cache = SimpleCache(ttl_seconds=300)
        cache.set("key1", {"data": "value"})

        result = cache.get("key1")

        assert result == {"data": "value"}

    def test_cache_miss_returns_none(self):
        cache = SimpleCache(ttl_seconds=300)

        result = cache.get("nonexistent")

        assert result is None

    def test_cache_clear_removes_all_entries(self):
        cache = SimpleCache(ttl_seconds=300)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None


# --- SwapiClient tests ---


class TestSwapiClient:
    @pytest.mark.asyncio
    async def test_fetch_character_returns_complete_data(
        self, mock_swapi, swapi_client
    ):
        """Verify that fetching a character returns all expected fields."""
        character = await swapi_client.get_character(1)

        assert character.name == "Luke Skywalker"
        assert character.height == "172"
        assert character.mass == "77"
        assert character.hair_color == "blond"
        assert character.gender == "male"
        assert character.birth_year == "19BBY"
        assert character.homeworld_url == "https://swapi.dev/api/planets/1/"

    @pytest.mark.asyncio
    async def test_fetch_character_with_homeworld_enriches_planet_data(
        self, mock_swapi, swapi_client
    ):
        """Verify that include_homeworld actually fetches and attaches planet."""
        character = await swapi_client.get_character_with_homeworld(1)

        assert character.homeworld is not None
        assert character.homeworld.name == "Tatooine"
        assert character.homeworld.climate == "arid"
        assert character.homeworld.terrain == "desert"

    @pytest.mark.asyncio
    async def test_fetch_character_404_raises_not_found_error(
        self, mock_swapi, swapi_client
    ):
        """Verify that fetching a non-existent character raises proper error."""
        with pytest.raises(SwapiNotFoundError) as exc_info:
            await swapi_client.get_character(999)

        assert exc_info.value.resource_type == "character"
        assert exc_info.value.resource_id == 999
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_fetch_planet_returns_expected_data(self, mock_swapi, swapi_client):
        """Verify planet data is parsed correctly."""
        planet = await swapi_client.get_planet(1)

        assert planet.name == "Tatooine"
        assert planet.population == "200000"
        assert planet.diameter == "10465"
        assert len(planet.resident_urls) == 2

    @pytest.mark.asyncio
    async def test_fetch_starship_returns_expected_data(self, mock_swapi, swapi_client):
        """Verify starship data is parsed correctly."""
        starship = await swapi_client.get_starship(10)

        assert starship.name == "Millennium Falcon"
        assert starship.model == "YT-1300 light freighter"
        assert starship.hyperdrive_rating == "0.5"
        assert starship.starship_class == "Light freighter"

    @pytest.mark.asyncio
    async def test_fetch_film_returns_expected_data(self, mock_swapi, swapi_client):
        """Verify film data is parsed correctly."""
        film = await swapi_client.get_film(1)

        assert film.title == "A New Hope"
        assert film.episode_id == 4
        assert film.director == "George Lucas"
        assert film.release_date == "1977-05-25"

    @pytest.mark.asyncio
    async def test_get_character_films_returns_film_summaries(
        self, mock_swapi, swapi_client
    ):
        """Verify that getting character films returns proper summaries."""
        films = await swapi_client.get_character_films(1)

        # Luke is in 3 films according to our mock data
        assert len(films) == 3
        # First film should be A New Hope
        assert films[0].title == "A New Hope"
        assert films[0].episode_id == 4

    @pytest.mark.asyncio
    async def test_get_planet_residents_returns_character_summaries(
        self, mock_swapi, swapi_client
    ):
        """Verify that getting planet residents returns proper summaries."""
        residents = await swapi_client.get_planet_residents(1)

        assert len(residents) == 2
        assert residents[0].name == "Luke Skywalker"

    @pytest.mark.asyncio
    async def test_extract_id_from_url(self, swapi_client):
        """Verify URL ID extraction works for various formats."""
        assert swapi_client._extract_id_from_url("https://swapi.dev/api/people/1/") == 1
        assert (
            swapi_client._extract_id_from_url("https://swapi.dev/api/planets/123/")
            == 123
        )
        assert (
            swapi_client._extract_id_from_url("https://swapi.dev/api/films/6") == 6
        )  # Without trailing slash

    @pytest.mark.asyncio
    async def test_extract_id_from_invalid_url_raises_error(self, swapi_client):
        """Verify invalid URLs raise ValueError."""
        with pytest.raises(ValueError):
            swapi_client._extract_id_from_url("https://swapi.dev/api/people/")

        with pytest.raises(ValueError):
            swapi_client._extract_id_from_url("invalid-url")


class TestSwapiClientRetry:
    @pytest.mark.asyncio
    async def test_timeout_triggers_retry(self):
        """Verify that timeouts trigger retry logic."""
        import httpx

        client = SwapiClient(cache_ttl=0)

        with respx.mock(base_url="https://swapi.dev/api") as mock:
            # First two calls timeout, third succeeds
            mock.get("/people/1/").mock(
                side_effect=[
                    httpx.TimeoutException("timeout"),
                    httpx.TimeoutException("timeout"),
                    Response(
                        200,
                        json={
                            "name": "Luke",
                            "height": "172",
                            "mass": "77",
                            "hair_color": "blond",
                            "skin_color": "fair",
                            "eye_color": "blue",
                            "birth_year": "19BBY",
                            "gender": "male",
                            "homeworld": "https://swapi.dev/api/planets/1/",
                            "films": [],
                            "species": [],
                            "vehicles": [],
                            "starships": [],
                            "url": "https://swapi.dev/api/people/1/",
                        },
                    ),
                ]
            )

            character = await client.get_character(1)
            assert character.name == "Luke"

        await client.close()

    @pytest.mark.asyncio
    async def test_max_retries_exceeded_raises_timeout_error(self):
        """Verify that exceeding max retries raises SwapiTimeoutError."""
        import httpx

        client = SwapiClient(cache_ttl=0)

        with respx.mock(base_url="https://swapi.dev/api") as mock:
            # All calls timeout
            mock.get("/people/1/").mock(
                side_effect=httpx.TimeoutException("timeout")
            )

            with pytest.raises(SwapiTimeoutError) as exc_info:
                await client.get_character(1)

            assert exc_info.value.attempts == 3  # Default max retries

        await client.close()


class TestSwapiClientCache:
    @pytest.mark.asyncio
    async def test_cache_returns_cached_data(self):
        """Verify that second request uses cached data."""
        client = SwapiClient(cache_ttl=300)  # 5 minute TTL

        with respx.mock(base_url="https://swapi.dev/api") as mock:
            mock.get("/people/1/").mock(
                return_value=Response(
                    200,
                    json={
                        "name": "Luke Skywalker",
                        "height": "172",
                        "mass": "77",
                        "hair_color": "blond",
                        "skin_color": "fair",
                        "eye_color": "blue",
                        "birth_year": "19BBY",
                        "gender": "male",
                        "homeworld": "https://swapi.dev/api/planets/1/",
                        "films": [],
                        "species": [],
                        "vehicles": [],
                        "starships": [],
                        "url": "https://swapi.dev/api/people/1/",
                    },
                )
            )

            # First call - hits API
            char1 = await client.get_character(1)
            # Second call - should use cache
            char2 = await client.get_character(1)

            assert char1.name == char2.name
            # Verify only one request was made
            assert mock.calls.call_count == 1

        await client.close()

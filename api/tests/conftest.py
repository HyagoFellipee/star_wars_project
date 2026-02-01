import pytest
import respx
from httpx import Response

from src.services.swapi_client import SwapiClient


# --- Sample SWAPI data ---
# Using actual data structure from SWAPI for realistic testing

LUKE_SKYWALKER = {
    "name": "Luke Skywalker",
    "height": "172",
    "mass": "77",
    "hair_color": "blond",
    "skin_color": "fair",
    "eye_color": "blue",
    "birth_year": "19BBY",
    "gender": "male",
    "homeworld": "https://swapi.dev/api/planets/1/",
    "films": [
        "https://swapi.dev/api/films/1/",
        "https://swapi.dev/api/films/2/",
        "https://swapi.dev/api/films/3/",
    ],
    "species": [],
    "vehicles": [
        "https://swapi.dev/api/vehicles/14/",
        "https://swapi.dev/api/vehicles/30/",
    ],
    "starships": [
        "https://swapi.dev/api/starships/12/",
        "https://swapi.dev/api/starships/22/",
    ],
    "created": "2014-12-09T13:50:51.644000Z",
    "edited": "2014-12-20T21:17:56.891000Z",
    "url": "https://swapi.dev/api/people/1/",
}

TATOOINE = {
    "name": "Tatooine",
    "rotation_period": "23",
    "orbital_period": "304",
    "diameter": "10465",
    "climate": "arid",
    "gravity": "1 standard",
    "terrain": "desert",
    "surface_water": "1",
    "population": "200000",
    "residents": [
        "https://swapi.dev/api/people/1/",
        "https://swapi.dev/api/people/2/",
    ],
    "films": [
        "https://swapi.dev/api/films/1/",
        "https://swapi.dev/api/films/3/",
    ],
    "created": "2014-12-09T13:50:49.641000Z",
    "edited": "2014-12-20T20:58:18.411000Z",
    "url": "https://swapi.dev/api/planets/1/",
}

A_NEW_HOPE = {
    "title": "A New Hope",
    "episode_id": 4,
    "opening_crawl": "It is a period of civil war...",
    "director": "George Lucas",
    "producer": "Gary Kurtz, Rick McCallum",
    "release_date": "1977-05-25",
    "characters": [
        "https://swapi.dev/api/people/1/",
        "https://swapi.dev/api/people/2/",
    ],
    "planets": [
        "https://swapi.dev/api/planets/1/",
    ],
    "starships": [
        "https://swapi.dev/api/starships/2/",
        "https://swapi.dev/api/starships/3/",
    ],
    "vehicles": [],
    "species": [],
    "created": "2014-12-10T14:23:31.880000Z",
    "edited": "2014-12-20T19:49:45.256000Z",
    "url": "https://swapi.dev/api/films/1/",
}

EMPIRE_STRIKES_BACK = {
    "title": "The Empire Strikes Back",
    "episode_id": 5,
    "opening_crawl": "It is a dark time for the Rebellion...",
    "director": "Irvin Kershner",
    "producer": "Gary Kurtz, Rick McCallum",
    "release_date": "1980-05-17",
    "characters": ["https://swapi.dev/api/people/1/"],
    "planets": [],
    "starships": [],
    "vehicles": [],
    "species": [],
    "created": "2014-12-12T11:26:24.656000Z",
    "edited": "2014-12-15T13:07:53.386000Z",
    "url": "https://swapi.dev/api/films/2/",
}

RETURN_OF_THE_JEDI = {
    "title": "Return of the Jedi",
    "episode_id": 6,
    "opening_crawl": "Luke Skywalker has returned to his home planet...",
    "director": "Richard Marquand",
    "producer": "Howard G. Kazanjian, George Lucas, Rick McCallum",
    "release_date": "1983-05-25",
    "characters": ["https://swapi.dev/api/people/1/"],
    "planets": [],
    "starships": [],
    "vehicles": [],
    "species": [],
    "created": "2014-12-18T10:39:33.255000Z",
    "edited": "2014-12-20T09:48:37.462000Z",
    "url": "https://swapi.dev/api/films/3/",
}

MILLENNIUM_FALCON = {
    "name": "Millennium Falcon",
    "model": "YT-1300 light freighter",
    "manufacturer": "Corellian Engineering Corporation",
    "cost_in_credits": "100000",
    "length": "34.37",
    "max_atmosphering_speed": "1050",
    "crew": "4",
    "passengers": "6",
    "cargo_capacity": "100000",
    "consumables": "2 months",
    "hyperdrive_rating": "0.5",
    "MGLT": "75",
    "starship_class": "Light freighter",
    "pilots": [
        "https://swapi.dev/api/people/13/",
        "https://swapi.dev/api/people/14/",
    ],
    "films": [
        "https://swapi.dev/api/films/1/",
        "https://swapi.dev/api/films/2/",
    ],
    "created": "2014-12-10T16:59:45.094000Z",
    "edited": "2014-12-20T21:23:49.880000Z",
    "url": "https://swapi.dev/api/starships/10/",
}

PEOPLE_LIST_PAGE_1 = {
    "count": 82,
    "next": "https://swapi.dev/api/people/?page=2",
    "previous": None,
    "results": [
        LUKE_SKYWALKER,
        {
            "name": "C-3PO",
            "height": "167",
            "mass": "75",
            "hair_color": "n/a",
            "skin_color": "gold",
            "eye_color": "yellow",
            "birth_year": "112BBY",
            "gender": "n/a",
            "homeworld": "https://swapi.dev/api/planets/1/",
            "films": ["https://swapi.dev/api/films/1/"],
            "species": ["https://swapi.dev/api/species/2/"],
            "vehicles": [],
            "starships": [],
            "url": "https://swapi.dev/api/people/2/",
        },
    ],
}


# --- Fixtures ---


@pytest.fixture
def swapi_client():
    """Create a fresh SWAPI client for each test."""
    return SwapiClient(cache_ttl=0)  # Disable cache for tests


@pytest.fixture
def mock_swapi():
    """
    Mock SWAPI endpoints with respx.

    Usage:
        def test_something(mock_swapi, swapi_client):
            # mock_swapi is already active
            ...
    """
    with respx.mock(base_url="https://swapi.dev/api", assert_all_called=False) as mock:
        # People endpoints
        mock.get("/people/1/").mock(return_value=Response(200, json=LUKE_SKYWALKER))
        mock.get("/people/2/").mock(
            return_value=Response(200, json=PEOPLE_LIST_PAGE_1["results"][1])
        )
        mock.get("/people/").mock(return_value=Response(200, json=PEOPLE_LIST_PAGE_1))
        mock.get("/people/?page=1").mock(
            return_value=Response(200, json=PEOPLE_LIST_PAGE_1)
        )
        mock.get("/people/999/").mock(return_value=Response(404))

        # Planet endpoints
        mock.get("/planets/1/").mock(return_value=Response(200, json=TATOOINE))
        mock.get("/planets/999/").mock(return_value=Response(404))

        # Film endpoints
        mock.get("/films/1/").mock(return_value=Response(200, json=A_NEW_HOPE))
        mock.get("/films/2/").mock(return_value=Response(200, json=EMPIRE_STRIKES_BACK))
        mock.get("/films/3/").mock(return_value=Response(200, json=RETURN_OF_THE_JEDI))
        mock.get("/films/999/").mock(return_value=Response(404))

        # Starship endpoints
        mock.get("/starships/10/").mock(
            return_value=Response(200, json=MILLENNIUM_FALCON)
        )
        mock.get("/starships/999/").mock(return_value=Response(404))

        yield mock


@pytest.fixture
def luke_data():
    """Raw Luke Skywalker data."""
    return LUKE_SKYWALKER


@pytest.fixture
def tatooine_data():
    """Raw Tatooine data."""
    return TATOOINE


@pytest.fixture
def film_data():
    """Raw A New Hope data."""
    return A_NEW_HOPE

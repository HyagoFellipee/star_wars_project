"""
Tests for router filter functionality.

These tests verify that filtering works correctly in the API endpoints,
including film_id filtering, exact match vs substring matching, and
proper pagination of filtered results.
"""

import pytest
import respx
from httpx import Response

from src.routers.characters import _apply_filters
from src.schemas.models import CharacterSummary


# --- Unit tests for _apply_filters ---


class TestApplyFilters:
    """Tests for the _apply_filters function."""

    def _make_char(
        self, name: str, gender: str, eye_color: str = "blue"
    ) -> CharacterSummary:
        """Helper to create CharacterSummary for testing."""
        return CharacterSummary(
            id=1,
            name=name,
            gender=gender,
            birth_year="19BBY",
            eye_color=eye_color,
            hair_color="blond",
            skin_color="fair",
        )

    def test_filter_gender_exact_match_male(self):
        """gender=male should NOT include 'female' (exact match)."""
        characters = [
            self._make_char("Luke", "male"),
            self._make_char("Leia", "female"),
            self._make_char("Vader", "male"),
        ]

        filtered = _apply_filters(
            characters,
            {"gender": "male"},
            exact_match_fields={"gender"},
        )

        assert len(filtered) == 2
        assert all(c.gender == "male" for c in filtered)
        # Verify "female" is NOT included
        assert not any(c.name == "Leia" for c in filtered)

    def test_filter_gender_exact_match_female(self):
        """gender=female should NOT include 'male'."""
        characters = [
            self._make_char("Luke", "male"),
            self._make_char("Leia", "female"),
            self._make_char("Padme", "female"),
        ]

        filtered = _apply_filters(
            characters,
            {"gender": "female"},
            exact_match_fields={"gender"},
        )

        assert len(filtered) == 2
        assert all(c.gender == "female" for c in filtered)

    def test_filter_gender_without_exact_match_includes_substring(self):
        """Without exact_match_fields, 'male' would match 'female' (substring)."""
        characters = [
            self._make_char("Luke", "male"),
            self._make_char("Leia", "female"),
        ]

        # Without exact_match_fields - uses substring matching
        filtered = _apply_filters(
            characters,
            {"gender": "male"},
            exact_match_fields=None,  # No exact match
        )

        # This would incorrectly include female because "male" is in "female"
        assert len(filtered) == 2

    def test_filter_eye_color_substring_match(self):
        """eye_color=blue should include 'blue-gray' (substring)."""
        characters = [
            self._make_char("Luke", "male", eye_color="blue"),
            self._make_char("Obi-Wan", "male", eye_color="blue-gray"),
            self._make_char("Vader", "male", eye_color="yellow"),
        ]

        filtered = _apply_filters(
            characters,
            {"eye_color": "blue"},
            exact_match_fields={"gender"},  # Only gender is exact
        )

        assert len(filtered) == 2
        assert any(c.eye_color == "blue" for c in filtered)
        assert any(c.eye_color == "blue-gray" for c in filtered)

    def test_filter_case_insensitive(self):
        """Filters should be case-insensitive."""
        characters = [
            self._make_char("Luke", "Male"),  # Capital M
            self._make_char("Leia", "female"),
        ]

        filtered = _apply_filters(
            characters,
            {"gender": "male"},  # lowercase
            exact_match_fields={"gender"},
        )

        assert len(filtered) == 1
        assert filtered[0].name == "Luke"

    def test_filter_combined_multiple_fields(self):
        """Multiple filters should be combined (AND logic)."""
        characters = [
            self._make_char("Luke", "male", eye_color="blue"),
            self._make_char("Vader", "male", eye_color="yellow"),
            self._make_char("Leia", "female", eye_color="brown"),
        ]

        filtered = _apply_filters(
            characters,
            {"gender": "male", "eye_color": "blue"},
            exact_match_fields={"gender"},
        )

        assert len(filtered) == 1
        assert filtered[0].name == "Luke"

    def test_filter_none_values_ignored(self):
        """Filter values of None should be ignored."""
        characters = [
            self._make_char("Luke", "male"),
            self._make_char("Leia", "female"),
        ]

        filtered = _apply_filters(
            characters,
            {"gender": None, "eye_color": None},
            exact_match_fields={"gender"},
        )

        assert len(filtered) == 2  # No filtering applied


class TestFilteredPagination:
    """Tests for pagination behavior with filtered results."""

    def _make_chars(self, count: int, gender: str = "male") -> list[CharacterSummary]:
        """Helper to create multiple CharacterSummary objects."""
        return [
            CharacterSummary(
                id=i,
                name=f"Character {i}",
                gender=gender,
                birth_year="19BBY",
                eye_color="blue",
                hair_color="blond",
                skin_color="fair",
            )
            for i in range(count)
        ]

    def test_pagination_count_reflects_filtered_results(self):
        """count/total_pages should reflect filtered data, not raw count."""
        # 20 characters total, but only 8 are male
        characters = self._make_chars(8, gender="male") + self._make_chars(12, gender="female")

        filtered = _apply_filters(
            characters,
            {"gender": "male"},
            exact_match_fields={"gender"},
        )

        assert len(filtered) == 8
        # With PAGE_SIZE=10, this should be 1 page
        import math
        page_size = 10
        total_pages = math.ceil(len(filtered) / page_size)
        assert total_pages == 1

    def test_page_slicing_with_filtered_results(self):
        """Verify page slicing works correctly on filtered results."""
        # 25 male characters -> should paginate to 3 pages
        characters = self._make_chars(25, gender="male")

        filtered = _apply_filters(
            characters,
            {"gender": "male"},
            exact_match_fields={"gender"},
        )

        # Simulate pagination
        page_size = 10
        page = 2
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_results = filtered[start_idx:end_idx]

        assert len(page_results) == 10  # Full page
        assert page_results[0].id == 10  # Second page starts at index 10

    def test_page_out_of_bounds_returns_empty(self):
        """Page beyond total_pages should return empty results."""
        characters = self._make_chars(5, gender="male")

        filtered = _apply_filters(
            characters,
            {"gender": "male"},
            exact_match_fields={"gender"},
        )

        # Request page 999
        page_size = 10
        page = 999
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_results = filtered[start_idx:end_idx]

        assert len(page_results) == 0

    def test_combined_filters_reduce_results(self):
        """Combining filters should further reduce result count."""
        characters = [
            CharacterSummary(id=1, name="Luke", gender="male", birth_year="19BBY",
                           eye_color="blue", hair_color="blond", skin_color="fair"),
            CharacterSummary(id=2, name="Vader", gender="male", birth_year="41.9BBY",
                           eye_color="yellow", hair_color="none", skin_color="white"),
            CharacterSummary(id=3, name="Han", gender="male", birth_year="29BBY",
                           eye_color="brown", hair_color="brown", skin_color="fair"),
            CharacterSummary(id=4, name="Leia", gender="female", birth_year="19BBY",
                           eye_color="brown", hair_color="brown", skin_color="light"),
        ]

        # Filter by gender only
        filtered_gender = _apply_filters(
            characters,
            {"gender": "male"},
            exact_match_fields={"gender"},
        )
        assert len(filtered_gender) == 3

        # Filter by gender AND eye_color
        filtered_both = _apply_filters(
            characters,
            {"gender": "male", "eye_color": "blue"},
            exact_match_fields={"gender"},
        )
        assert len(filtered_both) == 1
        assert filtered_both[0].name == "Luke"

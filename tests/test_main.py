import pytest


class TestRegionsQ:
    """q — fuzzy search. Minimum of 3 characters, case-insensitive; if q is provided, other parameters are ignored."""

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param(("Новосибирск", None, None, None), id="mixed case, full word"),
            pytest.param(("нов", None, None, None), id="lower case, fuzzy, len=3 (valid boundary)"),
            pytest.param(("НОВ", None, None, None), id="upper case, fuzzy"),
            pytest.param(("ново", None, None, None), id="len=4 (just above boundary)"),
        ],
        indirect=True,
    )
    def test_param_q(self, region_response):
        """Requirement 1: q — fuzzy search, case-insensitive."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' not in data
        assert 'items' in data
        assert isinstance(data['items'], list)
        assert len(data['items']) > 0
        assert data['total'] >= len(data['items'])

        seen = set()
        for item in data['items']:
            assert 'id' in item
            assert 'name' in item
            assert "нов" in item['name'].lower()
            assert item['id'] not in seen, f"Duplicate id in items: {item['id']}"
            seen.add(item['id'])

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param(("мо", None, None, None), id="len=2 (boundary invalid)"),
            pytest.param(("м", None, None, None), id="len=1 (invalid)"),
            pytest.param(("", None, None, None), id="len=0 (empty string)"),
            pytest.param(("   ", None, None, None), id="only spaces"),
        ],
        indirect=True,
    )
    def test_q_min_length_invalid(self, region_response):
        """Requirement 2: q shorter than 3 characters returns a validation error."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" in data
        assert data['error']['message'] == "Параметр 'q' должен быть не менее 3 символов"

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param(("нов", "ru", None, None), id="q + country_code"),
            pytest.param(("Нов", None, 1, None), id="q + page_size"),
            pytest.param(("нОв", None, None, 2), id="q + page"),
            pytest.param(("ноВ", "us", 1, 2), id="q + all params"),
        ],
        indirect=True,
    )
    def test_q_ignores_other_params_fuzzy(self, region_response):
        """Requirement 3 (fuzzy q): other parameters are ignored — proven by result count."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' not in data
        assert len(data['items']) > 1, (
            "page_size/country_code must be ignored when q is present: "
            "expected more than 1 item for fuzzy q='нов'"
        )

        names = [item['name'] for item in data['items']]
        assert "Новосибирск" in names, (
            "Extra params must be ignored: 'Новосибирск' should be returned by q alone"
        )

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param(("Новосибирск", "us", None, None), id="q + country_code"),
            pytest.param(("Новосибирск", None, None, 2), id="q + page"),
            pytest.param(("Новосибирск", "us", None, 2), id="q + country_code + page"),
        ],
        indirect=True,
    )
    def test_q_ignores_other_params_exact(self, region_response):
        """Requirement 3 (exact q): other parameters are ignored — proven by presence of exact match."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' not in data

        names = [item['name'] for item in data['items']]
        assert "Новосибирск" in names, (
            "Extra params must be ignored: 'Новосибирск' should be returned by q alone"
        )

class TestRegionsCountryCode:
    """country_code — filter by country. Allowed values: ru, kg, kz, cz. Default: no filter (all countries)."""

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, "ru", None, None), id="country_code=ru"),
            pytest.param((None, "kg", None, None), id="country_code=kg"),
            pytest.param((None, "kz", None, None), id="country_code=kz"),
            pytest.param((None, "cz", None, None), id="country_code=cz"),
        ],
        indirect=True,
    )
    def test_country_code_valid_values(self, region_response):
        """Requirement 1: each valid country_code returns items filtered to a single country."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' not in data
        assert 'items' in data
        assert isinstance(data['items'], list)
        assert len(data['items']) > 0

        country_codes = {item['country']['code'] for item in data['items']}
        assert len(country_codes) == 1, (
            f"All items must belong to a single country, got: {country_codes}"
        )

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, None, None, None), id="country_code not provided"
                                                      " (default: all countries)"),
        ],
        indirect=True,
    )
    def test_country_code_default(self, region_response):
        """Requirement 2: without country_code, response is successful and items are returned."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' not in data
        assert 'items' in data
        assert len(data['items']) > 0

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, "us", None, None), id="country_code=us (undocumented)"),
            pytest.param((None, "de", None, None), id="country_code=de (undocumented)"),
            pytest.param((None, "xx", None, None), id="country_code=xx (non-existent)"),
        ],
        indirect=True,
    )
    def test_country_code_undocumented_invalid(self, region_response):
        """Requirement 3: country_code outside the allowed set (ru/kg/kz/cz) returns a validation error."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' in data

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, "", None, None), id="country_code='' (empty string)"),
        ],
        indirect=True,
    )
    def test_country_code_empty_invalid(self, region_response):
        """Requirement 4: empty country_code returns a validation error."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' in data

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, "RU", None, None), id="country_code='RU' (uppercase)"),
            pytest.param((None, "Ru", None, None), id="country_code='Ru' (mixed case)"),
        ],
        indirect=True,
    )
    def test_country_code_case_sensitive_invalid(self, region_response):
        """Requirement 5: country_code is documented in lowercase — uppercase/mixed case returns a validation error."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' in data

class TestRegionsPage:
    """page — sequential page number. Minimum value = 1, default value = 1."""

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, None, None, 1), id="page=1 (min valid boundary)"),
        ],
        indirect=True,
    )
    def test_page_min_boundary_valid(self, region_response):
        """Requirement 1: page=1 is the minimum valid boundary — response is successful with items."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' not in data
        assert 'items' in data
        assert isinstance(data['items'], list)
        assert len(data['items']) > 0

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, None, None, None), id="page not provided (default=1)"),
        ],
        indirect=True,
    )
    def test_page_default_value(self, region_response):
        """Requirement 2: default page is 1 — request without page returns valid data."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' not in data
        assert 'items' in data
        assert len(data['items']) > 0

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, None, None, 2), id="page=2 (typical valid)"),
            pytest.param((None, None, None, 3), id="page=3 (typical valid)"),
        ],
        indirect=True,
    )
    def test_page_valid_positive(self, region_response):
        """Requirement 3: any positive integer above min is a valid page — response schema is valid."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' not in data
        assert 'items' in data
        assert isinstance(data['items'], list)

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, None, None, 0), id="page=0 (invalid boundary, below min)"),
            pytest.param((None, None, None, -1), id="page=-1 (negative)"),
        ],
        indirect=True,
    )
    def test_page_below_min_invalid(self, region_response):
        """Requirement 4: page < 1 returns a validation error."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' in data

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, None, None, "abc"), id="page='abc' (non-numeric)"),
            pytest.param((None, None, None, "1.5"), id="page='1.5' (float string)"),
        ],
        indirect=True,
    )
    def test_page_non_integer_invalid(self, region_response):
        """Requirement 5: non-integer page returns a validation error."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' in data


class TestRegionsPageSize:
    """page_size — items per page. Allowed values: 5, 10, 15. Default value: 15."""

    @pytest.mark.parametrize(
        "region_response, expected_size",
        [
            pytest.param((None, None, 5, None), 5, id="page_size=5"),
            pytest.param((None, None, 10, None), 10, id="page_size=10"),
            pytest.param((None, None, 15, None), 15, id="page_size=15"),
        ],
        indirect=["region_response"],
    )
    def test_page_size_valid_values(self, region_response, expected_size):
        """Requirement 1: valid page_size (5/10/15) returns exactly page_size items on the first page."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' not in data
        assert len(data['items']) == expected_size

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, None, None, None), id="page_size not provided (default=15)"),
        ],
        indirect=True,
    )
    def test_page_size_default_value(self, region_response):
        """Requirement 2: default page_size is 15 — request without page_size returns 15 items."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' not in data
        assert len(data['items']) == 15

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, None, 1, None), id="page_size=1 (below allowed set)"),
            pytest.param((None, None, 20, None), id="page_size=20 (above allowed set)"),
            pytest.param((None, None, 100, None), id="page_size=100 (far above allowed set)"),
        ],
        indirect=True,
    )
    def test_page_size_undocumented_invalid(self, region_response):
        """Requirement 3: page_size outside {5, 10, 15} returns a validation error."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' in data

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, None, 0, None), id="page_size=0 (invalid boundary)"),
            pytest.param((None, None, -1, None), id="page_size=-1 (negative)"),
            pytest.param((None, None, -5, None), id="page_size=-5 (negative)"),
        ],
        indirect=True,
    )
    def test_page_size_non_positive_invalid(self, region_response):
        """Requirement 4: page_size <= 0 returns a validation error."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' in data

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param((None, None, "abc", None), id="page_size='abc' (non-numeric)"),
            pytest.param((None, None, "5.5", None), id="page_size='5.5' (float string)"),
        ],
        indirect=True,
    )
    def test_page_size_non_integer_invalid(self, region_response):
        """Requirement 5: non-integer page_size returns a validation error."""
        status_code, data = region_response
        assert status_code == 200
        assert 'error' in data

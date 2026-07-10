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
            pytest.param(("но", None, None, None), id="len=2 (boundary invalid)"),
            pytest.param(("н", None, None, None), id="len=1 (invalid)"),
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
            pytest.param(("нов", "us", None, None), id="q + country_code"),
            pytest.param(("нов", None, 1, None), id="q + page_size"),
            pytest.param(("нов", None, None, 2), id="q + page"),
            pytest.param(("нов", "us", 1, 2), id="q + all params"),
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
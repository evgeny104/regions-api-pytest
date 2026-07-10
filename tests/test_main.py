import pytest

class TestRegionsQ:
    """q — fuzzy search. Minimum of 3 characters, case-insensitive; if q is provided, other parameters are ignored."""
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param(("Новосибирск", None, None, None)),
            pytest.param(("нов", None, None, None)),
            pytest.param(("НОВ", None, None, None)),
            pytest.param(("Нов", None, None, None)),
        ],
        # parameterized fixture
        indirect=True
    )
    def test_param_q(self, region_response):
        """Requirement 1: q — fuzzy search."""
        status_code, data = region_response
        assert status_code == 200
        assert data is not None

        for item in data['items']:
            assert "нов" in item['name'].lower()


    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param(("н", None, None, None)),
            pytest.param(("но", None, None, None)),
        ],
        indirect=True
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
            # Pairwise — комбинации q с каждым параметром по отдельности
            pytest.param(("Новосибирск", "us", None, None)),  # q + чужой country_code
            pytest.param(("Новосибирск", None, 1, None)),  # q + минимальный page_size
            pytest.param(("Новосибирск", None, None, 2)),  # q + page=2

            # Pairwise — комбинации двух параметров
            pytest.param(("Новосибирск", "us", 1, None)),  # q + country_code + page_size
            pytest.param(("Новосибирск", "us", None, 2)),  # q + country_code + page
            pytest.param(("Новосибирск", None, 1, 2)),  # q + page_size + page

            # All combinations — все параметры сразу
            pytest.param(("Новосибирск", "us", 1, 2)),  # q + все параметры

            # Boundary values — граничные значения page_size и page
            pytest.param(("Новосибирск", None, 0, None)),  # page_size=0 (граница снизу)
            pytest.param(("Новосибирск", None, 999, None)),  # page_size=999 (граница сверху)
            pytest.param(("Новосибирск", None, None, 0)),  # page=0 (граница снизу)
            pytest.param(("Новосибирск", None, None, 999)),  # page=999 (граница сверху)
        ],
        indirect=True
    )
    def test_q_ignores_other_params(self, region_response):
        """Requirement 3: If q is passed, the other parameters are ignored."""
        status_code, data = region_response
        assert status_code == 200
        names = [item['name'] for item in data['items']]
        assert "Новосибирск" in names




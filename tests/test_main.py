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
        indirect=True
    )
    def test_param_q(self, region_response):
        status_code, data = region_response
        assert status_code == 200





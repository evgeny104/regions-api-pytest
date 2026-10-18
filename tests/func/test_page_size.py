import pytest


class TestRegionsPageSize:
    """page_size — элементов на страницу. Допустимые значения: 5, 10, 15. По умолчанию: 15."""

    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "region_response, expected_size",
        [
            pytest.param({"page_size": 5},  5,  id="page_size=5"),
            pytest.param({"page_size": 10}, 10, id="page_size=10"),
            pytest.param({"page_size": 15}, 15, id="page_size=15"),
        ],
        indirect=["region_response"],
    )
    def test_page_size_valid_values(self, region_response, expected_size):
        """Требование 1: валидный page_size (5/10/15) возвращает ровно page_size элементов на первой странице."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" not in data
        assert len(data["items"]) == expected_size, (
            f"ожидали ровно {expected_size} элементов, получили {len(data['items'])}"
        )

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({}, id="page_size не передан (default=15)"),
        ],
        indirect=True,
    )
    def test_page_size_default_value(self, region_response):
        """Требование 2: значение page_size по умолчанию = 15 — запрос без page_size возвращает 15 элементов."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" not in data
        assert len(data["items"]) == 15

    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"page_size": 1},   id="page_size=1 (ниже допустимого множества)"),
            pytest.param({"page_size": 20},  id="page_size=20 (выше допустимого множества)"),
            pytest.param({"page_size": 100}, id="page_size=100 (сильно выше множества)"),
        ],
        indirect=True,
    )
    def test_page_size_undocumented_invalid(self, region_response):
        """Требование 3: page_size вне множества {5, 10, 15} возвращает ошибку с заполненными id и message."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" in data
        assert data["error"]["id"]
        assert data["error"]["message"]

    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"page_size": 0},  id="page_size=0 (невалидная граница)"),
            pytest.param({"page_size": -1}, id="page_size=-1 (отрицательный)"),
            pytest.param({"page_size": -5}, id="page_size=-5 (отрицательный)"),
        ],
        indirect=True,
    )
    def test_page_size_non_positive_invalid(self, region_response):
        """Требование 4: page_size <= 0 возвращает ошибку с заполненными id и message."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" in data
        assert data["error"]["id"]
        assert data["error"]["message"]

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"page_size": "abc"}, id="page_size='abc' (нечисло)"),
            pytest.param({"page_size": "5.5"}, id="page_size='5.5' (строка с дробью)"),
        ],
        indirect=True,
    )
    def test_page_size_non_integer_invalid(self, region_response):
        """Требование 5: нецелочисленный page_size возвращает ошибку с заполненными id и message."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" in data
        assert data["error"]["id"]
        assert data["error"]["message"]

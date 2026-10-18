import pytest


class TestRegionsCombinedValidParams:
    """Комбинации валидных параметров без q: country_code + page + page_size."""

    @pytest.mark.combined
    @pytest.mark.parametrize(
        "region_response, expected_country, expected_size",
        [
            pytest.param({"country_code": "ru", "page_size": 5},            "ru", 5,
                         id="ru + page_size=5"),
            pytest.param({"country_code": "cz", "page": 1, "page_size": 5}, "cz", 5,
                         id="cz + page=1 + page_size=5"),
        ],
        indirect=["region_response"],
    )
    def test_country_and_pagination_together(self, region_response, expected_country, expected_size):
        """Все элементы соответствуют запрошенному country_code; количество элементов не превышает page_size."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" not in data
        assert 0 < len(data["items"]) <= expected_size

        for item in data["items"]:
            assert item["country"]["code"] == expected_country, (
                f"страна элемента {item['country']['code']!r} не совпадает с запрошенной {expected_country!r}"
            )

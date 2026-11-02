import pytest


class TestRegionsCombinedValidParams:
    """Комбинации валидных параметров без q: country_code + page + page_size."""

    @pytest.mark.combined
    @pytest.mark.parametrize(
        "region_response, expected_country, expected_size",
        [
            pytest.param({"country_code": "ru", "page": 1, "page_size": 5}, "ru", 5,
                         id="ru + page_size=5"),
            pytest.param({"country_code": "ru", "page": 1, "page_size": 10}, "ru", 10,
                         id="ru + page_size=10"),
            pytest.param({"country_code": "ru", "page": 1, "page_size": 15}, "ru", 15,
                         id="ru + page_size=15"),
            pytest.param(
                {"country_code": "kg", "page": 1, "page_size": 5}, "kg", 5,
                id="kg + page_size=5",
                marks=pytest.mark.xfail(
                    reason="BUG-002: фильтр country_code=kg возвращает элементы с кодом kz",
                    strict=True,
                ),
            ),
            pytest.param(
                {"country_code": "kg", "page": 1, "page_size": 10}, "kg", 10,
                id="kg + page_size=10",
                marks=pytest.mark.xfail(
                    reason="BUG-002: фильтр country_code=kg возвращает элементы с кодом kz",
                    strict=True,
                ),
            ),
            pytest.param(
                {"country_code": "kg", "page": 1, "page_size": 15}, "kg", 15,
                id="kg + page_size=15",
                marks=pytest.mark.xfail(
                    reason="BUG-002: фильтр country_code=kg возвращает элементы с кодом kz",
                    strict=True,
                ),
            ),
            pytest.param(
                {"country_code": "kz", "page": 1, "page_size": 5}, "kz", 5,
                id="kz + page_size=5",
                marks=pytest.mark.xfail(
                    reason="BUG-002: фильтр country_code=kz возвращает элементы с кодом kg",
                    strict=True,
                ),
            ),
            pytest.param(
                {"country_code": "kz", "page": 1, "page_size": 10}, "kz", 10,
                id="kz + page_size=10",
                marks=pytest.mark.xfail(
                    reason="BUG-002: фильтр country_code=kz возвращает элементы с кодом kg",
                    strict=True,
                ),
            ),
            pytest.param(
                {"country_code": "kz", "page": 1, "page_size": 15}, "kz", 15,
                id="kz + page_size=15",
                marks=pytest.mark.xfail(
                    reason="BUG-002: фильтр country_code=kz возвращает элементы с кодом kg",
                    strict=True,
                ),
            ),
            pytest.param({"country_code": "cz", "page": 1, "page_size": 5}, "cz", 5,
                         id="cz + page=1 + page_size=5"),
            pytest.param({"country_code": "cz", "page": 1, "page_size": 10}, "cz", 10,
                         id="cz + page=1 + page_size=10"),
            pytest.param({"country_code": "cz", "page": 1, "page_size": 15}, "cz", 15,
                         id="cz + page=1 + page_size=15"),
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

import pytest


class TestRegionsCountryCode:
    """country_code — фильтр по стране. Допустимые значения: ru, kg, kz, cz. По умолчанию — без фильтра (все страны)."""

    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "region_response, expected_country",
        [
            pytest.param({"country_code": "ru"}, "ru", id="country_code=ru"),
            pytest.param({"country_code": "kg"}, "kg", id="country_code=kg"),
            pytest.param({"country_code": "kz"}, "kz", id="country_code=kz"),
            pytest.param({"country_code": "cz"}, "cz", id="country_code=cz"),
        ],
        indirect=["region_response"],
    )
    def test_country_code_valid_values(self, region_response, expected_country):
        """Требование 1: каждое валидное country_code возвращает items, отфильтрованные по запрошенной стране."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" not in data
        assert len(data["items"]) > 0

        for item in data["items"]:
            assert item["country"]["code"] == expected_country, (
                f"страна элемента {item['country']['code']!r} не совпадает с запрошенной {expected_country!r}"
            )

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({}, id="country_code не передан (default: все страны)"),
        ],
        indirect=True,
    )
    def test_country_code_default(self, region_response):
        """Требование 2: без country_code ответ успешен и элементы возвращаются."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" not in data
        assert len(data["items"]) > 0

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"country_code": "us"}, id="country_code=us (не документирован)"),
            pytest.param({"country_code": "de"}, id="country_code=de (не документирован)"),
            pytest.param({"country_code": "xx"}, id="country_code=xx (несуществующий)"),
        ],
        indirect=True,
    )
    def test_country_code_undocumented_invalid(self, region_response):
        """Требование 3: country_code вне допустимого множества (ru/kg/kz/cz) возвращает ошибку с заполненными id и message."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" in data
        assert data["error"]["id"], "error.id не должен быть пустым"
        assert data["error"]["message"], "error.message не должен быть пустым"

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"country_code": ""}, id="country_code='' (пустая строка)"),
        ],
        indirect=True,
    )
    def test_country_code_empty_invalid(self, region_response):
        """Требование 4: пустой country_code возвращает ошибку с заполненными id и message."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" in data
        assert data["error"]["id"]
        assert data["error"]["message"]

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"country_code": "RU"}, id="country_code='RU' (верхний регистр)"),
            pytest.param({"country_code": "Ru"}, id="country_code='Ru' (смешанный регистр)"),
        ],
        indirect=True,
    )
    def test_country_code_case_sensitive_invalid(self, region_response):
        """Требование 5: country_code документирован в lowercase — uppercase/mixed case возвращает ошибку с заполненными id и message."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" in data
        assert data["error"]["id"]
        assert data["error"]["message"]

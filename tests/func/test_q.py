import pytest


class TestRegionsQ:
    """q — fuzzy-поиск. Минимум 3 символа, регистронезависимый; если q задан, остальные параметры игнорируются."""

    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"q": "Новосибирск"}, id="смешанный регистр, слово целиком"),
            pytest.param({"q": "нов"},         id="нижний регистр, fuzzy, len=3 (валидная граница)"),
            pytest.param({"q": "НОВ"},         id="верхний регистр, fuzzy"),
            pytest.param({"q": "ново"},        id="len=4 (чуть выше границы)"),
        ],
        indirect=True,
    )
    def test_param_q(self, region_response):
        """Требование 1: q — fuzzy-поиск, регистронезависимый."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" not in data
        assert len(data["items"]) > 0, "fuzzy q должен возвращать хотя бы один элемент"
        assert data["total"] >= len(data["items"]), "total должен быть >= количества возвращённых элементов"

        seen = set()
        for item in data["items"]:
            assert "нов" in item["name"].lower(), (
                f"имя {item['name']!r} не содержит fuzzy-подстроку 'нов'"
            )
            assert item["id"] not in seen, f"дубликат id в items: {item['id']}"
            seen.add(item["id"])

    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"q": "мо"},  id="len=2 (невалидная граница)"),
            pytest.param({"q": "м"},   id="len=1 (невалидно)"),
            pytest.param({"q": ""},    id="len=0 (пустая строка)"),
            pytest.param({"q": "   "}, id="только пробелы"),
        ],
        indirect=True,
    )
    def test_q_min_length_invalid(self, region_response):
        """Требование 2: q короче 3 символов возвращает ошибку валидации с конкретным сообщением."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" in data
        assert data["error"]["message"] == "Параметр 'q' должен быть не менее 3 символов"
        assert data["error"]["id"], "error.id не должен быть пустым"

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"q": "нов", "country_code": "ru"},                              id="q + country_code"),
            pytest.param({"q": "Нов", "page_size": 1},                                    id="q + page_size"),
            pytest.param({"q": "нОв", "page": 2},                                         id="q + page"),
            pytest.param({"q": "ноВ", "country_code": "us", "page": 2, "page_size": 1},   id="q + все параметры"),
        ],
        indirect=True,
    )
    def test_q_ignores_other_params_fuzzy(self, region_response):
        """Требование 3 (fuzzy q): прочие параметры игнорируются — проверяем по количеству результатов."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" not in data
        assert len(data["items"]) > 1, (
            "page_size/country_code должны игнорироваться при наличии q: "
            "ожидали больше одного элемента для fuzzy q='нов'"
        )

        names = [item["name"] for item in data["items"]]
        assert "Новосибирск" in names, (
            "дополнительные параметры должны игнорироваться: 'Новосибирск' должен возвращаться по одному q"
        )

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"q": "Новосибирск", "country_code": "us"},              id="q + country_code"),
            pytest.param({"q": "Новосибирск", "page": 2},                         id="q + page"),
            pytest.param({"q": "Новосибирск", "country_code": "us", "page": 2},   id="q + country_code + page"),
        ],
        indirect=True,
    )
    def test_q_ignores_other_params_exact(self, region_response):
        """Требование 3 (exact q): прочие параметры игнорируются — проверяем по наличию точного совпадения."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" not in data

        names = [item["name"] for item in data["items"]]
        assert "Новосибирск" in names, (
            "дополнительные параметры должны игнорироваться: 'Новосибирск' должен возвращаться по одному q"
        )

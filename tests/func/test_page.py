import pytest


class TestRegionsPage:
    """page — номер страницы. Минимальное значение = 1, значение по умолчанию = 1."""

    @pytest.mark.smoke
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"page": 1}, id="page=1 (валидная граница min)"),
        ],
        indirect=True,
    )
    def test_page_min_boundary_valid(self, region_response):
        """Требование 1: page=1 — минимальная валидная граница, ответ успешен с элементами."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" not in data
        assert len(data["items"]) > 0

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({}, id="page не передан (default=1)"),
        ],
        indirect=True,
    )
    def test_page_default_value(self, region_response):
        """Требование 2: значение page по умолчанию = 1 — запрос без page возвращает валидные данные."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" not in data
        assert len(data["items"]) > 0

    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"page": 2}, id="page=2 (типичный валидный)"),
            pytest.param({"page": 3}, id="page=3 (типичный валидный)"),
        ],
        indirect=True,
    )
    def test_page_valid_positive(self, region_response):
        """Требование 3: любое целое больше минимума — валидная страница, items не пуст (при достаточном total)."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" not in data
        assert len(data["items"]) > 0, (
            f"валидная страница вернула пустой items (total={data['total']}) — "
            "выбирай page с заведомо достаточным total"
        )

    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"page": 0},  id="page=0 (невалидная граница, ниже min)"),
            pytest.param({"page": -1}, id="page=-1 (отрицательный)"),
        ],
        indirect=True,
    )
    def test_page_below_min_invalid(self, region_response):
        """Требование 4: page < 1 возвращает ошибку с заполненными id и message."""
        status_code, data = region_response
        assert status_code == 200
        assert "error" in data
        assert data["error"]["id"]
        assert data["error"]["message"]

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"page": "abc"}, id="page='abc' (нечисло)"),
            pytest.param({"page": "1.5"}, id="page='1.5' (строка с дробью)"),
        ],
        indirect=True,
    )
    def test_page_non_integer_invalid(self, region_response):
        """Требование 5: нецелочисленный page возвращает ошибку с заполненными id и message."""
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
            pytest.param({"page": 99999}, id="page=99999 (далеко за пределами total)"),
        ],
        indirect=True,
    )
    def test_page_above_total(self, region_response):
        """Требование 6: page сильно выше количества страниц — либо ошибка валидации, либо пустой items.

        Контракт API формально не прописан; тест фиксирует фактическое поведение
        и ловит регрессию (например, 500 вместо пустого ответа).
        """
        status_code, data = region_response
        assert status_code == 200
        if "error" in data:
            assert data["error"]["id"]
            assert data["error"]["message"]
        else:
            assert data["items"] == [], (
                f"ожидали либо ошибку, либо пустой items; получили {len(data['items'])} элементов"
            )

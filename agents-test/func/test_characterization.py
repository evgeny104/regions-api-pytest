import math

import pytest


class TestRegionsCharacterization:
    """Дополнительные characterization-сценарии; они не добавляют требования контракту."""

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"page": 1}, id="characterization page=1"),
            pytest.param({}, id="characterization page по умолчанию"),
        ],
        indirect=True,
    )
    def test_page_minimum_and_default(self, region_response):
        """Characterization из user suite: page=1 и default дают успешные данные."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" not in data
        assert data["items"]

    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"page": 0}, id="characterization page=0"),
            pytest.param({"page": -1}, id="characterization page=-1"),
        ],
        indirect=True,
    )
    def test_page_below_minimum(self, region_response):
        """Characterization из user suite: ниже предполагаемого min возвращается error."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" in data
        assert data["error"]["id"]
        assert data["error"]["message"]

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"page": "abc"}, id="characterization page не число"),
            pytest.param({"page": "1.5"}, id="characterization page дробь"),
        ],
        indirect=True,
    )
    def test_page_non_integer(self, region_response):
        """Characterization из user suite: нецелое значение page возвращает error."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" in data
        assert data["error"]["id"]
        assert data["error"]["message"]

    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "region_response",
        [pytest.param({"page": 99999}, id="characterization page за пределами выдачи")],
        indirect=True,
    )
    def test_page_above_total(self, region_response):
        """Characterization допускает error body или пустой список вне диапазона."""
        status_code, data = region_response

        assert status_code == 200
        if "error" in data:
            assert data["error"]["id"]
            assert data["error"]["message"]
        else:
            assert data["items"] == []

    @pytest.mark.parametrize(
        "region_response, expected_size",
        [
            pytest.param({"page_size": 5}, 5, id="documented page_size=5"),
            pytest.param({"page_size": 10}, 10, id="characterization page_size=10"),
            pytest.param({"page_size": 15}, 15, id="characterization page_size=15"),
        ],
        indirect=["region_response"],
    )
    def test_page_size_values(self, region_response, expected_size):
        """Characterization: страница содержит ожидаемое число items для выбранного размера."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" not in data
        assert len(data["items"]) == expected_size

    @pytest.mark.parametrize(
        "region_response",
        [pytest.param({}, id="characterization default page_size=15")],
        indirect=True,
    )
    def test_page_size_default(self, region_response):
        """Characterization из user suite: default page_size даёт 15 элементов."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" not in data
        assert len(data["items"]) == 15

    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"page_size": 1}, id="characterization page_size=1"),
            pytest.param({"page_size": 20}, id="characterization page_size=20"),
            pytest.param({"page_size": 100}, id="characterization page_size=100"),
            pytest.param({"page_size": 0}, id="characterization page_size=0"),
            pytest.param({"page_size": -1}, id="characterization page_size=-1"),
            pytest.param({"page_size": -5}, id="characterization page_size=-5"),
        ],
        indirect=True,
    )
    def test_page_size_non_positive_or_undocumented(self, region_response):
        """Characterization из user suite: размер вне набора возвращает заполненную error."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" in data
        assert data["error"]["id"]
        assert data["error"]["message"]

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"page_size": "abc"}, id="characterization page_size не число"),
            pytest.param({"page_size": "5.5"}, id="characterization page_size дробь"),
        ],
        indirect=True,
    )
    def test_page_size_non_integer(self, region_response):
        """Characterization из user suite: нецелое page_size возвращает error."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" in data
        assert data["error"]["id"]
        assert data["error"]["message"]

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"q": "a"}, id="characterization q length=1"),
            pytest.param({"q": "ab"}, id="characterization q length=2"),
            pytest.param({"q": ""}, id="characterization q пустой"),
            pytest.param({"q": "   "}, id="characterization q пробелы"),
        ],
        indirect=True,
    )
    def test_q_minimum_and_blank_values(self, region_response):
        """Characterization из user suite: короткий или пустой q возвращает заданную error."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" in data
        assert data["error"]["message"] == "Параметр 'q' должен быть не менее 3 символов"
        assert data["error"]["id"]

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param({"country_code": "us"}, id="characterization country_code=us"),
            pytest.param({"country_code": "de"}, id="characterization country_code=de"),
            pytest.param({"country_code": "xx"}, id="characterization country_code=xx"),
            pytest.param({"country_code": ""}, id="characterization country_code пустой"),
            pytest.param({"country_code": "RU"}, id="characterization country_code=RU"),
            pytest.param({"country_code": "Ru"}, id="characterization country_code=Ru"),
        ],
        indirect=True,
    )
    def test_undocumented_country_code_values(self, region_response):
        """Characterization из user suite: неизвестный код страны возвращает error."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" in data
        assert data["error"]["id"]
        assert data["error"]["message"]

    @pytest.mark.combined
    @pytest.mark.parametrize(
        "region_response, expected_country, expected_size",
        [
            pytest.param(
                {"country_code": code, "page": 1, "page_size": size}, code, size,
                id=f"characterization {code} + page_size={size}",
            )
            for code in ("ru", "kg", "kz", "cz")
            for size in (5, 10, 15)
        ],
        indirect=["region_response"],
    )
    def test_country_filter_combined_with_page_size(
        self, region_response, expected_country, expected_size
    ):
        """Characterization из user suite: country_code и page_size применяются вместе."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" not in data
        assert 0 < len(data["items"]) <= expected_size
        assert all(
            item["country"]["code"] == expected_country for item in data["items"]
        )

    @pytest.mark.pagination
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "page_size",
        [
            pytest.param(5, id="characterization last page_size=5"),
            pytest.param(10, id="characterization last page_size=10"),
            pytest.param(15, id="characterization last page_size=15"),
        ],
    )
    def test_last_page_contains_expected_remainder(self, regions_request, page_size):
        """Characterization из user suite: последняя страница содержит математический остаток."""
        first_status, first_data = regions_request(
            {"page": 1, "page_size": page_size}, label="[последняя страница: первая]"
        )
        assert first_status == 200
        assert "error" not in first_data
        total = first_data["total"]
        last_page = math.ceil(total / page_size)
        expected_count = total - (last_page - 1) * page_size

        last_status, last_data = regions_request(
            {"page": last_page, "page_size": page_size},
            label=f"[последняя страница: page={last_page}]",
        )
        assert last_status == 200
        assert "error" not in last_data
        assert last_data["total"] == total
        assert len(last_data["items"]) == expected_count, (
            f"последняя страница page={last_page} ожидала {expected_count} элементов, "
            f"получено {len(last_data['items'])}"
        )

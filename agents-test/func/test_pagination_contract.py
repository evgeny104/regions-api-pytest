import pytest


class TestRegionsPaginationContract:
    """Порядковый номер страницы и количество элементов по примеру API."""

    @pytest.mark.pagination
    @pytest.mark.parametrize(
        "region_response_pair",
        [
            pytest.param(
                (
                    {"page": 2, "page_size": 5},
                    {"page": 3, "page_size": 5},
                ),
                id="документированные page=2 и page=3, page_size=5",
            ),
        ],
        indirect=True,
    )
    def test_page_number_changes_selected_result(self, region_response_pair):
        """API-002/012: порядковый номер выбирает другую выдачу, total стабилен."""
        (status_a, data_a), (status_b, data_b) = region_response_pair

        assert status_a == 200 and status_b == 200
        assert "error" not in data_a and "error" not in data_b
        assert data_a["items"] and data_b["items"]
        assert data_a["total"] == data_b["total"], (
            "total должен быть общим количеством записей, а не числом текущей страницы"
        )
        assert data_a["total"] > len(data_a["items"]), (
            "total должен включать записи вне текущей страницы"
        )

        ids_a = {item["id"] for item in data_a["items"]}
        ids_b = {item["id"] for item in data_b["items"]}
        assert ids_a != ids_b, (
            f"разные значения page должны выбирать разные выдачи: {ids_a} == {ids_b}"
        )

    @pytest.mark.pagination
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param(
                {"page": 3, "page_size": 5},
                id="пример запроса page=3&page_size=5",
            ),
        ],
        indirect=True,
    )
    def test_documented_page_size_controls_full_page(self, region_response):
        """API-013: документированный page_size=5 задаёт размер полной страницы."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" not in data
        assert len(data["items"]) == 5, (
            f"полная страница с page_size=5 должна содержать 5 элементов, "
            f"получено {len(data['items'])}"
        )

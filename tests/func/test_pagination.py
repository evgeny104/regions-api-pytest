import pytest


class TestRegionsPagination:
    """Поведение пагинации: последовательные страницы должны возвращать непересекающиеся элементы и стабильный total."""

    @pytest.mark.pagination
    @pytest.mark.parametrize(
        "region_response_pair",
        [
            pytest.param(
                ({"page": 1, "page_size": 5}, {"page": 2, "page_size": 5}),
                id="page_size=5, страница 1 vs страница 2",
            ),
            pytest.param(
                ({"page": 1, "page_size": 10}, {"page": 2, "page_size": 10}),
                id="page_size=10, страница 1 vs страница 2",
            ),
            pytest.param(
                ({"country_code": "ru", "page": 1, "page_size": 5},
                 {"country_code": "ru", "page": 2, "page_size": 5}),
                id="country_code=ru, page_size=5, страница 1 vs страница 2",
            ),
        ],
        indirect=True,
    )
    def test_pages_are_disjoint_and_total_stable(self, region_response_pair):
        """Две последовательные страницы с одним page_size возвращают разные элементы; total не меняется."""
        (status_a, data_a), (status_b, data_b) = region_response_pair
        assert status_a == 200 and status_b == 200
        assert "error" not in data_a and "error" not in data_b
        assert len(data_a["items"]) > 0 and len(data_b["items"]) > 0

        assert data_a["total"] == data_b["total"], (
            f"total должен быть стабилен между страницами: {data_a['total']} vs {data_b['total']}"
        )

        ids_a = {item["id"] for item in data_a["items"]}
        ids_b = {item["id"] for item in data_b["items"]}
        overlap = ids_a & ids_b
        assert not overlap, f"последовательные страницы вернули пересекающиеся id: {overlap}"

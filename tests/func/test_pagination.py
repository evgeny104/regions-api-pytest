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

    @pytest.mark.pagination
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "page_size",
        [
            pytest.param(
                5,
                id="page_size=5",
                marks=pytest.mark.xfail(
                    reason="BUG-001: последняя страница возвращает 5 элементов вместо остатка 2 (дубликаты из предыдущих страниц)",
                    strict=True,
                ),
            ),
            pytest.param(
                10,
                id="page_size=10",
                marks=pytest.mark.xfail(
                    reason="BUG-001: последняя страница возвращает 3 элемента вместо остатка 2",
                    strict=True,
                ),
            ),
            pytest.param(15, id="page_size=15"),
        ],
    )
    def test_last_page_returns_remainder(self, regions_request, page_size):
        """Последняя страница возвращает остаток `0 < len(items) <= page_size`; total стабилен.

        Защита от off-by-one: страница `ceil(total/page_size)` должна содержать
        ровно `total - (last_page - 1) * page_size` элементов.
        """
        _, data_first = regions_request({"page_size": page_size, "page": 1}, label="[page=1]")
        assert "error" not in data_first
        total = data_first["total"]
        assert total > 0, "ожидали непустой total для расчёта последней страницы"

        last_page = (total + page_size - 1) // page_size
        expected_last_count = total - (last_page - 1) * page_size

        _, data_last = regions_request(
            {"page_size": page_size, "page": last_page}, label=f"[page={last_page}]"
        )
        assert "error" not in data_last
        assert data_last["total"] == total, (
            f"total должен быть стабилен между страницами: {total} vs {data_last['total']}"
        )
        assert len(data_last["items"]) == expected_last_count, (
            f"на последней странице ожидали {expected_last_count} элементов "
            f"(total={total}, page_size={page_size}, last_page={last_page}), "
            f"получили {len(data_last['items'])}"
        )

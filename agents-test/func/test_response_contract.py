import math

import pytest


class TestRegionsResponseContract:
    """Поля и значения ответа из примера контракта."""

    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "region_response",
        [
            pytest.param(
                {"q": "Новосибирск"},
                id="контрактный пример: Новосибирск",
            ),
        ],
        indirect=True,
    )
    def test_documented_region_fields_and_values(self, region_response):
        """API-001/004/005/006: схема и значения объекта Новосибирска."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" not in data
        assert type(data["total"]) is int
        assert isinstance(data["items"], list)
        assert data["items"]

        example = next(
            (item for item in data["items"] if item["name"] == "Новосибирск"),
            None,
        )
        assert example is not None, "в ответе должен быть контрактный пример региона"
        assert example["code"] == "novosibirsk"
        assert example["country"]["name"] == "Россия"
        assert example["country"]["code"] == "ru"

    def test_total_stays_stable_when_page_changes(self, regions_request):
        """API-002: total остаётся общим числом базы при запросе другой страницы."""
        first_status, first_data = regions_request(
            {"page": 1, "page_size": 5}, label="[page=1]"
        )
        second_status, second_data = regions_request(
            {"page": 2, "page_size": 5}, label="[page=2]"
        )

        assert first_status == 200 and second_status == 200
        assert "error" not in first_data and "error" not in second_data
        assert first_data["total"] == second_data["total"], (
            "total должен обозначать общее число регионов, а не размер страницы"
        )

    def test_total_stays_stable_across_page_sizes(self, regions_request):
        """API-002b: сравнительная проверка total для разных размеров страницы."""
        totals = {}
        for page_size in (5, 10, 15):
            status_code, data = regions_request(
                {"page_size": page_size}, label=f"[total, page_size={page_size}]"
            )
            assert status_code == 200
            assert "error" not in data
            totals[page_size] = data["total"]

        assert len(set(totals.values())) == 1, (
            f"API-002b/characterization: total меняется вместе с page_size: {totals}"
        )

    def test_total_with_country_filter_characterization(self, regions_request):
        """API-002c characterization: фиксирует total с фильтром страны из user suite."""
        baseline_status, baseline = regions_request(
            {"page_size": 5}, label="[total без country_code]"
        )
        filtered_status, filtered = regions_request(
            {"country_code": "ru", "page_size": 5},
            label="[total с country_code=ru]",
        )

        assert baseline_status == 200 and filtered_status == 200
        assert "error" not in baseline and "error" not in filtered
        assert filtered["total"] == baseline["total"], (
            "characterization из сравнительного сценария: total одинаков "
            f"до/после country_code=ru ({baseline['total']} != {filtered['total']})"
        )

    @pytest.mark.parametrize(
        "page_size",
        [pytest.param(5, id="документированный page_size=5")],
    )
    def test_ids_are_unique_within_each_sampled_page(self, regions_request, page_size):
        """API-003: в каждой наблюдаемой выдаче ID регионов не повторяются."""
        first_status, first_data = regions_request(
            {"page": 1, "page_size": page_size}, label="[уникальность id, page=1]"
        )
        assert first_status == 200
        assert "error" not in first_data
        page_count = math.ceil(first_data["total"] / page_size)

        for page in range(1, page_count + 1):
            if page == 1:
                status_code, data = first_status, first_data
            else:
                status_code, data = regions_request(
                    {"page": page, "page_size": page_size},
                    label=f"[уникальность id, page={page}]",
                )

            assert status_code == 200
            assert "error" not in data
            ids = [item["id"] for item in data["items"]]
            assert len(ids) == len(set(ids)), (
                f"на странице {page} повторяются идентификаторы: {ids}"
            )

    @pytest.mark.pagination
    def test_ids_keep_the_same_entity_across_pages(self, regions_request):
        """API-003b: один ID между страницами всегда соответствует одной сущности."""
        page_size = 5
        first_status, first_data = regions_request(
            {"page": 1, "page_size": page_size}, label="[id -> entity, page=1]"
        )
        assert first_status == 200
        assert "error" not in first_data
        page_count = math.ceil(first_data["total"] / page_size)
        entities_by_id = {}

        for page in range(1, page_count + 1):
            if page == 1:
                status_code, data = first_status, first_data
            else:
                status_code, data = regions_request(
                    {"page": page, "page_size": page_size},
                    label=f"[id -> entity, page={page}]",
                )

            assert status_code == 200
            assert "error" not in data
            for item in data["items"]:
                entity = (
                    item["name"],
                    item["code"],
                    item["country"]["name"],
                    item["country"]["code"],
                )
                previous_entity = entities_by_id.setdefault(item["id"], entity)
                assert previous_entity == entity, (
                    f"id={item['id']} указывает на разные сущности: "
                    f"{previous_entity!r} и {entity!r}"
                )

    @pytest.mark.parametrize(
        "region_response",
        [pytest.param({}, id="учебный пример задания: total=22")],
        indirect=True,
    )
    def test_total_matches_assignment_example(self, region_response):
        """API-014: проверяет ожидаемое число из примера теста задания."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" not in data
        assert data["total"] == 22, (
            f"учебный пример задания ожидает total=22, получено {data['total']}"
        )

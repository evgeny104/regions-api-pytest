import pytest


class TestRegionsQContract:
    """Нечёткий поиск, регистр q и приоритет поискового параметра."""

    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "region_response",
        [pytest.param({"q": "рск"}, id="поиск по контрактной подстроке рск")],
        indirect=True,
    )
    def test_q_matches_requested_substring_and_examples(self, region_response):
        """API-007: результат содержит q в имени и контрактные примеры."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" not in data
        names = [item["name"] for item in data["items"]]
        assert names
        assert all("рск" in name.casefold() for name in names), (
            f"каждое имя должно содержать подстроку q='рск': {names}"
        )
        assert {"Новосибирск", "Магнитогорск", "Орск"} <= set(names), (
            "в примере контракта для q='рск' перечислены Новосибирск, "
            "Магнитогорск и Орск"
        )

    def test_q_results_do_not_depend_on_letter_case(self, regions_request):
        """API-008: изменение регистра поисковой строки не меняет выдачу."""
        lower_status, lower_data = regions_request({"q": "рск"}, label="[q lower]")
        upper_status, upper_data = regions_request({"q": "РСК"}, label="[q upper]")

        assert lower_status == 200 and upper_status == 200
        assert "error" not in lower_data and "error" not in upper_data
        lower_ids = {item["id"] for item in lower_data["items"]}
        upper_ids = {item["id"] for item in upper_data["items"]}
        assert lower_ids == upper_ids, (
            f"регистр q не должен менять набор результатов: {lower_ids} != {upper_ids}"
        )

    @pytest.mark.parametrize(
        "extra_params",
        [
            pytest.param({"country_code": "cz"}, id="игнорировать country_code"),
            pytest.param(
                {"country_code": "us"},
                id="игнорировать country_code=us",
            ),
            pytest.param({"page": 2}, id="игнорировать page"),
            pytest.param({"page_size": 1}, id="игнорировать page_size"),
            pytest.param(
                {"country_code": "cz", "page": 2, "page_size": 1},
                id="игнорировать остальные параметры вместе",
            ),
        ],
    )
    def test_q_ignores_other_query_parameters(self, regions_request, extra_params):
        """API-009: при наличии q прочие query-параметры игнорируются."""
        base_status, base_data = regions_request({"q": "рск"}, label="[только q]")
        combined_status, combined_data = regions_request(
            {"q": "рск", **extra_params}, label="[q и дополнительные параметры]"
        )

        assert base_status == 200 and combined_status == 200
        assert "error" not in base_data and "error" not in combined_data
        assert combined_data["total"] == base_data["total"], (
            "при наличии q игнорирование прочих параметров должно сохранять total"
        )
        base_ids = {item["id"] for item in base_data["items"]}
        combined_ids = {item["id"] for item in combined_data["items"]}
        assert combined_ids == base_ids, (
            "добавление других query-параметров не должно менять результаты q"
        )

import math

import pytest


class TestRegionsCountryCodeContract:
    """Допустимые коды стран и поведение фильтра по умолчанию."""

    @pytest.mark.parametrize(
        "region_response, expected_country",
        [
            pytest.param(
                {"country_code": "ru"}, "ru", id="допустимое значение ru"
            ),
            pytest.param(
                {"country_code": "kg"},
                "kg",
                id="допустимое значение kg",
                marks=pytest.mark.xfail(
                    reason=(
                        "BUG-004: country_code=kg возвращает смешанную выдачу "
                        "с country.code kz,kg"
                    ),
                    strict=True,
                ),
            ),
            pytest.param(
                {"country_code": "kz"},
                "kz",
                id="допустимое значение kz",
                marks=pytest.mark.xfail(
                    reason=(
                        "BUG-004: country_code=kz возвращает смешанную выдачу "
                        "с country.code kz,kg"
                    ),
                    strict=True,
                ),
            ),
            pytest.param(
                {"country_code": "cz"}, "cz", id="допустимое значение cz"
            ),
        ],
        indirect=["region_response"],
    )
    def test_country_code_filters_to_requested_country(
        self, region_response, expected_country
    ):
        """API-010: каждый допустимый код фильтрует элементы по стране."""
        status_code, data = region_response

        assert status_code == 200
        assert "error" not in data
        assert data["items"]
        assert all(
            item["country"]["code"] == expected_country for item in data["items"]
        ), f"каждый элемент должен принадлежать стране {expected_country}"

    def test_default_country_code_includes_documented_countries(
        self, regions_request
    ):
        """API-011 (частично): без фильтра выдача включает страны из списка контракта."""
        page_size = 5  # Документированный пример значения page_size.
        first_status, first_data = regions_request(
            {"page": 1, "page_size": page_size}, label="[без country_code, page=1]"
        )

        assert first_status == 200, (
            f"запрос без country_code на page=1 вернул status={first_status}, "
            f"error={first_data.get('error')}"
        )
        assert "error" not in first_data
        page_count = math.ceil(first_data["total"] / page_size)
        observed_codes = {
            item["country"]["code"] for item in first_data["items"]
        }

        for page in range(2, page_count + 1):
            status_code, data = regions_request(
                {"page": page, "page_size": page_size},
                label=f"[без country_code, page={page}]",
            )
            assert status_code == 200, (
                f"запрос без country_code на page={page} вернул status={status_code}, "
                f"error={data.get('error')}"
            )
            assert "error" not in data
            observed_codes.update(item["country"]["code"] for item in data["items"])

        expected_documented_codes = {"ru", "kg", "kz", "cz"}
        assert expected_documented_codes <= observed_codes, (
            "без country_code должны быть представлены страны, перечисленные "
            f"в контракте; отсутствуют {expected_documented_codes - observed_codes}"
        )

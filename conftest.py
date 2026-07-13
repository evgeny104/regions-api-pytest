import pytest
import allure
import requests as req_lib
from main import Region
from src.config.url import BASE_URL
from src.models.region import RegionResponse, RegionErrorResponse

@pytest.fixture
def region_response(request):
    q, country_code, page_size, page = request.param

    region = Region(
        url=BASE_URL,
        q=q,
        country_code=country_code,
        page_size=page_size,
        page=page
    )

    params = region.get_params()
    prepared = req_lib.Request('GET', BASE_URL.rstrip('?'), params=params).prepare()
    full_url = prepared.url

    allure.dynamic.parameter("URL", full_url)
    for key, value in params.items():
        allure.dynamic.parameter(key, value)

    with allure.step(f"Send GET request with params: q={q}, country_code={country_code}, page_size={page_size},"
                     f" page={page}"):
        status_code, data = region.get_data()

    with allure.step("Attach API response to the report"):
        allure.attach(
            str(data),
            name="Response body",
            attachment_type=allure.attachment_type.TEXT
        )

    return status_code, data
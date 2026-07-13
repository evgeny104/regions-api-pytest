import pytest
import allure
import requests as req_lib
from main import Region
from src.config.url import BASE_URL
from src.models.Pydantic.region import RegionResponse, RegionErrorResponse

@pytest.fixture
def region_response(request):
    region = Region(url=BASE_URL, **request.param)

    params = region.get_params()
    prepared = req_lib.Request('GET', BASE_URL.rstrip('?'), params=params).prepare()
    full_url = prepared.url

    allure.dynamic.parameter("URL", full_url)
    for key, value in params.items():
        allure.dynamic.parameter(key, value)

    with allure.step(f"Send GET request with params: {request.param}"):
        status_code, data = region.get_data()

    with allure.step("Validate response body schema"):
        if "error" in data:
            validated = RegionErrorResponse(**data)
        else:
            validated = RegionResponse(**data)

    with allure.step("Attach API response to the report"):
        allure.attach(
            str(data),
            name="Response body",
            attachment_type=allure.attachment_type.TEXT
        )

    return status_code, validated.model_dump()
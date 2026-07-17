import pytest
import allure
import requests as req_lib
from main import Region
from src.config.url import BASE_URL
from src.models.Pydantic.region import RegionResponse, RegionErrorResponse


def _do_request(param, label=""):
    region = Region(url=BASE_URL, **param)

    params = region.get_params()
    prepared = req_lib.Request('GET', BASE_URL.rstrip('?'), params=params).prepare()
    full_url = prepared.url

    prefix = f"{label} " if label else ""
    allure.dynamic.parameter(f"{prefix}URL", full_url)
    for key, value in params.items():
        allure.dynamic.parameter(f"{prefix}{key}", value)

    with allure.step(f"Send GET request {prefix}with params: {param}"):
        status_code, data = region.get_data()

    with allure.step(f"Validate {prefix}response body schema"):
        if "error" in data:
            validated = RegionErrorResponse(**data)
        else:
            validated = RegionResponse(**data)

    with allure.step(f"Attach {prefix}API response to the report"):
        allure.attach(
            str(data),
            name=f"{prefix}Response body".strip(),
            attachment_type=allure.attachment_type.TEXT
        )

    return status_code, validated.model_dump()


@pytest.fixture(autouse=True)
def _allure_class_grouping(request):
    cls = request.cls
    if cls is None:
        return
    first_line = (cls.__doc__ or cls.__name__).strip().splitlines()[0]
    class_label = first_line.split('.')[0].strip()
    allure.dynamic.label("epic", "Regions API")
    allure.dynamic.label("feature", class_label)
    allure.dynamic.label("parentSuite", "Regions API")
    allure.dynamic.label("suite", class_label)
    allure.dynamic.label("package", f"{cls.__module__}.{cls.__name__}")


@pytest.fixture
def region_response(request):
    return _do_request(request.param)


@pytest.fixture
def region_response_pair(request):
    param_a, param_b = request.param
    return _do_request(param_a, label="[A]"), _do_request(param_b, label="[B]")
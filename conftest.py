import pytest
import allure
import requests as req_lib

from src.api.region_client import Region
from src.config.url import BASE_URL
from models.Pydantic.region import RegionResponse, RegionErrorResponse


@pytest.fixture(scope="session")
def base_url() -> str:
    """Эндпоинт под тестом. Session-scope — читается один раз за прогон."""
    return BASE_URL


@pytest.fixture
def regions_request(base_url):
    """Фикстура-фабрика: вызываем с dict'ом query-параметров и получаем валидированный ответ.

    Okken-style factory — позволяет собирать запросы инлайн без репараметризации
    фикстуры. Возвращает (status_code, data_dict), где data_dict — это Pydantic-модель,
    сброшенная обратно в dict через model_dump().
    """

    def _call(params: dict, label: str = ""):
        client = Region(url=base_url, **params)
        prepared_params = client.get_params()
        full_url = (
            req_lib.Request("GET", base_url.rstrip("?"), params=prepared_params)
            .prepare()
            .url
        )

        prefix = f"{label} " if label else ""
        allure.dynamic.parameter(f"{prefix}URL", full_url)
        for key, value in prepared_params.items():
            allure.dynamic.parameter(f"{prefix}{key}", value)

        with allure.step(f"GET {prefix}с параметрами: {params}"):
            status_code, data = client.get_data()

        with allure.step(f"Валидация схемы ответа {prefix}"):
            if "error" in data:
                validated = RegionErrorResponse(**data)
            else:
                validated = RegionResponse(**data)

        with allure.step(f"Прикрепить {prefix}тело ответа к отчёту"):
            allure.attach(
                str(data),
                name=f"{prefix}Response body".strip(),
                attachment_type=allure.attachment_type.TEXT,
            )

        return status_code, validated.model_dump()

    return _call


@pytest.fixture
def region_response(request, regions_request):
    """Indirect-фикстура — читает параметры из pytest.param и делает один запрос."""
    return regions_request(request.param)


@pytest.fixture
def region_response_pair(request, regions_request):
    """Indirect-фикстура — делает два запроса, используется для сравнения страниц пагинации."""
    params_a, params_b = request.param
    return (
        regions_request(params_a, label="[A]"),
        regions_request(params_b, label="[B]"),
    )


@pytest.fixture(autouse=True)
def _allure_class_grouping(request):
    """Автоматически проставляет epic/feature для каждого теста по docstring класса-владельца."""
    cls = request.cls
    if cls is None:
        return
    first_line = (cls.__doc__ or cls.__name__).strip().splitlines()[0]
    class_label = first_line.split(".")[0].strip()
    allure.dynamic.label("epic", "Regions API")
    allure.dynamic.label("feature", class_label)
    allure.dynamic.label("parentSuite", "Regions API")
    allure.dynamic.label("suite", class_label)
    allure.dynamic.label("package", f"{cls.__module__}.{cls.__name__}")

# Тесты Regions API

Автотесты 2GIS Regions API (`q`, `country_code`, `page`, `page_size`, комбинации, пагинация). Стиль — Okken: pytest + pydantic + allure, factory-фикстуры, маркеры, конфиг в `pyproject.toml`.

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate                   # Windows
# source .venv/bin/activate               # Linux/macOS
pip install -r requirements.txt
```

Создай `src/config/url.py` (gitignored):

```python
BASE_URL = 'https://host/1.0/regions'
```

## Запуск

Дефолты в `pyproject.toml` (`-v`, `--strict-markers`, `testpaths=tests`, `pythonpath=.`).

```bash
pytest                                   # все тесты
pytest tests/func                        # только API-тесты
pytest tests/unit                        # только unit (без сети)
pytest -k TestRegionsQ                   # один класс
pytest -m smoke                          # по маркеру
pytest --alluredir=allure-results        # с allure
```

### Маркеры

`smoke`, `negative`, `boundary`, `combined`, `pagination` — зарегистрированы в `pyproject.toml`.

```bash
pytest -m "negative and boundary"        # невалидные граничные значения
pytest -m "not negative"                 # всё, кроме негатива
```

### Windows: кириллица в выводе

```powershell
$env:PYTHONIOENCODING = "utf-8"
chcp 65001
```

## Allure

```bash
pytest --alluredir=allure-results
allure serve allure-results              # временный сервер
# или статическая сборка:
allure generate allure-results -o allure-report --clean
allure open allure-report
```

В отчёте: suites по классам (feature — из docstring класса), attachment `Response body` на каждом запросе, allure-параметры `URL`/`q`/`page`.

## Docker

```bash
docker build --build-arg BASE_URL=<BASE_URL> -t regions-tests .
docker run --rm -v "${PWD}/allure-results:/app/allure-results" regions-tests
```

## Структура

```
.
├── pyproject.toml                       # конфиг pytest
├── src/
│   ├── api/region_client.py             # обёртка над requests + классификация сетевых ошибок
│   └── config/url.py                    # BASE_URL (gitignored)
├── models/Pydantic/region.py            # Pydantic-схемы ответа
└── tests/
    ├── func/                            # API-тесты, по файлу на параметр
    │   ├── conftest.py                  # base_url, regions_request (factory), allure grouping
    │   └── test_*.py
    └── unit/
        └── test_region_client.py        # monkeypatch, без сети
```

## Соглашения

- Класс = параметр. Первая строка docstring класса → allure feature-label.
- `pytest.param(..., id="...")` с читаемыми русскими id (ASCII-escaping отключён).
- Фикстура `regions_request` возвращает `(status_code, data_dict)` — `data` это `model_dump()`, доступ через `data["items"]`.
- Негативные тесты проверяют конкретные `error.id` / `error.message`, где контракт известен.

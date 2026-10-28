# CLAUDE.md

Контекст проекта для Claude Code. Этот файл автоматически подтягивается в системный промпт.

## Что это

Автотесты публичного API `GET {BASE_URL}` (2GIS Regions API; значение `BASE_URL` — в gitignored `src/config/url.py`). Проверяют поведение query-параметров `q`, `country_code`, `page`, `page_size`, их комбинации и пагинацию.

## Стек

| Инструмент | Версия | Назначение |
|---|---|---|
| Python | 3.14 (venv `.venv`) | Runtime |
| pytest | 9.1.1 | Test runner |
| pydantic | 2.13.4 | Валидация схемы ответа |
| requests | 2.34.2 | HTTP-клиент |
| allure-pytest | 2.16.0 | Отчёты |
| allure-python-commons | — | Поддержка allure |

Конфиг pytest — в `pyproject.toml` (`testpaths=tests`, `pythonpath=.`, `--strict-markers`, `--strict-config`, `-v`).

## Запуск

Все команды — из корня проекта. Запускать **`pytest`** без `python -m`, чтобы ловить sys.path-баги так же, как CI.

```bash
# прогон всех тестов
pytest

# подмножества
pytest tests/func                    # только API-тесты (ходят в сеть)
pytest tests/unit                    # только unit (без сети)
pytest -m smoke                      # по маркеру
pytest -k TestRegionsPagination      # по имени класса

# прогон с Allure
pytest --alluredir=allure-results
allure serve allure-results          # временный веб-сервер с отчётом
# или статическая сборка:
allure generate allure-results -o allure-report --clean
allure open allure-report
```

Windows + кириллица в выводе:
```powershell
$env:PYTHONIOENCODING = "utf-8"
chcp 65001
```

Перед первым запуском создать `src/config/url.py` (gitignored):
```python
BASE_URL = '<полный адрес стенда>'
```

## Структура

```
regions-api-pytest/
├── pyproject.toml              # конфиг pytest + маркеры
├── requirements.txt
├── Dockerfile
├── CLAUDE.md
├── README.md
├── ТЗ.pdf                      # исходное ТЗ (в репо, через явное отключение ignore)
├── src/
│   ├── api/region_client.py    # класс Region: сборка params + GET + классификация сетевых ошибок
│   └── config/url.py           # BASE_URL (gitignored)
├── models/Pydantic/region.py   # схемы: RegionResponse, RegionErrorResponse
├── tests/
│   ├── func/                   # API-тесты (идут в сеть), по файлу на query-параметр
│   │   ├── conftest.py
│   │   ├── test_q.py
│   │   ├── test_country_code.py
│   │   ├── test_page.py
│   │   ├── test_page_size.py
│   │   ├── test_combined.py
│   │   └── test_pagination.py
│   └── unit/
│       └── test_region_client.py   # monkeypatch, без сети
├── bug-reports/                # markdown-репорты по найденным дефектам API
│   └── BUG-001-last-page-overflow.md
├── allure-results/             # сырые данные allure (gitignored)
└── allure-report/              # собранный HTML (gitignored)
```

## Маркеры

Зарегистрированы в `pyproject.toml` (`--strict-markers`, незнакомый маркер упадёт):

| Маркер | Назначение |
|---|---|
| `smoke` | Базовый happy-path, должен проходить всегда |
| `negative` | Ожидается ошибка валидации в теле ответа |
| `boundary` | Граничные значения (min, max, min−1, max+1) |
| `combined` | Комбинации нескольких query-параметров |
| `pagination` | Поведение пагинации на двух последовательных страницах |

Комбинируются выражениями: `pytest -m "negative and boundary"`, `pytest -m "not negative"`.

## Фикстуры

Все живут в `tests/func/conftest.py`.

| Фикстура | Scope | Тип | Что делает |
|---|---|---|---|
| `base_url` | session | обычная | Возвращает `BASE_URL` из `src/config/url.py`. |
| `regions_request` | function | factory | `_call(params: dict, label: str = "")` — делает GET, валидирует ответ через Pydantic (`RegionResponse` или `RegionErrorResponse`), прикладывает `URL`/параметры/тело к Allure, возвращает `(status_code, data_dict)`. Используется напрямую, когда тест двухфазный (параметры второго запроса зависят от первого). |
| `region_response` | function | indirect | Читает `pytest.param({...})`, делает один запрос через `regions_request`. Используется в большинстве параметризованных тестов. |
| `region_response_pair` | function | indirect | Читает `pytest.param((params_a, params_b))`, делает два запроса с лейблами `[A]`/`[B]`. Используется для сравнения страниц пагинации. |
| `_allure_class_grouping` | function | autouse | Автоматически проставляет `epic="Regions API"`, `feature`/`suite` из первой строки docstring класса-владельца. |

Юнит-тесты (`tests/unit/`) собственного `conftest.py` не имеют, используют только `pytest` + `monkeypatch`.

## Правила работы

1. **Перед тем как называть падение теста багом сервиса — свериться с заданием** (`ТЗ.pdf`). Поведение, которое не нарушает описанный контракт, — не баг, даже если оно выглядит неожиданным.
2. **Не ослаблять ассерты ради «зелёного» CI.** Для подтверждённых дефектов сервиса использовать `@pytest.mark.xfail(reason="BUG-XXX: …", strict=True)`, а не смягчать проверку.
3. **Не добавлять в тест фильтры (например `country_code`), которые ломают расчёт от `total`.** По ТЗ `total` — общее количество регионов в базе, фильтром не меняется; формулы вида `last_page = ceil(total / page_size)` при активном фильтре некорректны.
4. **Использовать только существующие маркеры и фикстуры** (см. разделы «Маркеры» и «Фикстуры» выше). Новый маркер — сначала зарегистрировать в `pyproject.toml` и сообщить мне до использования.
5. **Отвечать коротко: сначала вывод, потом детали.** Длинные пояснения — только по делу.
6. **Проверять орфографию коммит-сообщений** перед `git commit`: если в тексте, который ты даёшь, есть опечатка — сообщить и подождать подтверждения, не пропускать молча в репо.

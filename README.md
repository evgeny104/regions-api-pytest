# Regions API pytest demo

Демо-проект функционального тестирования REST API на Python, pytest и Pydantic. Он показывает проверяемый процесс:
извлечь требования из контракта, связать их с тест-сценариями, написать агентскую suite, независимо проверить покрытие и
зафиксировать результат.

## Что показывает проект

- Параметризованные API-тесты с pytest fixtures, клиентом `Region` и строгой Pydantic-валидацией.
- Контрактный тест-план с атомарными ID, техниками тест-дизайна и трассировкой до assertions.
- Четыре специализированные роли: checklist, author, read-only reviewer и bug reporter.
- Assertion mutation-check в агентской suite: временное нарушение проверки должно уронить тест на целевом assertion,
  затем исходный код восстанавливается.
- Раздельную классификацию подтверждённых нарушений контракта, characterization-наблюдений и инфраструктурных ошибок.

## Источники и границы

- `tz-extracted.txt` — источник требований API.
- `tests/func/` — пользовательские тесты, read-only ориентир стиля и глубины сценариев. Агенты их не изменяют и не
  запускают.
- `agents-test/` — все результаты агентского цикла: чек-лист, тесты и отчёты.
- Новые bug reports создаются только по текущим результатам `agents-test/func/`; исторические отчёты хранятся вместе в
  `agents-test/bug/` и не являются доказательствами для новых дефектов.
- Неоднозначные или не описанные контрактом проверки могут присутствовать как characterization, но не считаются
  требованиями API.

## Быстрый запуск

Создайте окружение и установите зависимости:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Укажите endpoint в локальном, некоммитируемом `src/config/url.py`:

```python
BASE_URL = "https://host/1.0/regions"
```

Запускайте suites отдельно, чтобы видеть их результаты независимо:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/func/
.\.venv\Scripts\python.exe -m pytest agents-test/func/
```

Обычный `pytest` запускает все директории из `testpaths` в `pyproject.toml`. Функциональные тесты обращаются к сетевому
API. Агентский полный цикл запускается только по явному запросу; author запускает `agents-test/func/`, делает
mutation/recovery checks и передаёт результат reviewer и bug reporter.

Для Allure:

```powershell
.\.venv\Scripts\python.exe -m pytest agents-test/func/ --alluredir=allure-results
allure serve allure-results
```

## Агентский цикл

1. `regions-api-checklist` анализирует контракт и сравнивает сценарии с пользовательской suite; меняет только
   `agents-test/checklist/api-checklist.md`.
2. `regions-test-author` реализует сценарии только в `agents-test/func/`, валидирует ответы общими fixtures/Pydantic и
   при поручении запускает/mutates только агентские тесты.
3. `regions-test-reviewer` read-only проверяет каждый применимый ID и возвращает конкретные пробелы автору.
4. `regions-api-bug-reporter` после прогона/ревью использует только лог `agents-test/func/` и пишет только в
   `agents-test/bug/YYYY-MM-DD/`.

Подробные правила живут в `.agents/skills/`; `.codex/agents/` содержит короткие описания ролей и ссылки на skills.

## Структура

```text
src/api/                  API-клиент
models/Pydantic/          Pydantic-модели ответов
tests/func/               пользовательская suite, read-only для агентов
agents-test/checklist/    контрактный план и карта покрытия
agents-test/func/         независимая агентская suite
agents-test/bug/          все отчёты по датам; новые — только по агентским прогонам
conftest.py               общие pytest fixtures
.agents/skills/           подробные процедуры ролей
.codex/agents/            описания специализированных агентов
.github/workflows/        GitHub Actions
```

Актуальные числа последнего агентского прогона и ограничения покрытия указаны в [NOTES.md](NOTES.md).

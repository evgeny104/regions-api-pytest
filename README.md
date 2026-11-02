# Regions API — functional testing demo

Демо-проект на Python и pytest для функционального тестирования REST API. Показывает
работу с API-клиентом, схемами Pydantic, параметризацией, фикстурами, Allure и
контрактными проверками.

## Что демонстрирует проект

- API-клиент на `requests` и модели ответов на Pydantic.
- Функциональные тесты поиска, фильтров, пагинации, граничных и комбинированных сценариев.
- pytest-маркеры, повторно используемые фикстуры и отчёты Allure.
- Строгие `xfail` для подтверждённых дефектов API и отдельные отчёты с шагами воспроизведения.
- AI-разработку: специализированные агенты для создания и ревью тестов, навыки и правила проекта.

## Стек

Python 3.14 · pytest · Requests · Pydantic · Allure · GitHub Actions · Docker

## Запуск

Создай виртуальное окружение и установи зависимости:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
. .\.venv\Scripts\Activate.ps1
```

Создай локальный файл `src/config/url.py` с адресом тестового API:

```python
BASE_URL = "https://host/1.0/regions"
```

Файл конфигурации игнорируется Git. Функциональные тесты обращаются к API по сети:

```bash
pytest
pytest -m smoke
pytest -m "negative and boundary"
pytest tests/func/test_pagination.py
pytest --alluredir=allure-results
```

Для просмотра отчёта установи Allure CLI и выполни `allure serve allure-results`.

GitHub Actions запускает функциональные тесты вручную. Добавь секрет `BASE_URL` в
репозиторий и выбери `smoke` или `all` при запуске workflow.

## AI-инструменты проекта

- `.codex/agents/` — агенты для написания и независимого ревью API-тестов.
- `.agents/skills/` — инструкции по тестам и оформлению подтверждённых дефектов.
- `AGENTS.md` — правила работы, источники контракта и маршрутизация задач.
- `NOTES.md` — снимок покрытия и бэклог улучшений.

## Структура

```text
src/api/                  API-клиент
models/Pydantic/          схемы ответов
tests/func/               функциональные API-тесты и фикстуры
bug/YYYY-MM-DD/           отчёты о подтверждённых дефектах
.agents/skills/           навыки и рабочие процессы
.codex/agents/            специализированные агенты
.github/workflows/        GitHub Actions
```

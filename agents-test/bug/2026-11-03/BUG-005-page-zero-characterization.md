# Наблюдение: `page=0` возвращает HTTP 500

**Классификация:** неподтверждённое characterization-ожидание; нарушение
контракта не установлено\
**Severity:** не определена\
**Priority:** не определён\
**Component:** `GET /1.0/regions`, параметр `page`\
**Env:** `{BASE_URL}`; Windows, Python 3.14.10, pytest 9.1.1\
**Reporter:** regions-api-bug-reporter\
**Date:** 2026-11-03

## Наблюдение

В агентском тесте с characterization-ожиданием для нулевой страницы API
вернул HTTP 500, тест ожидал HTTP 200 и отсутствие ошибки.

## Контракт и ограничение

`tz-extracted.txt`, стр. 2, указывает, что `page` — порядковый номер страницы,
но минимальное значение заменено NUL-символом. Контракт не задаёт поведение
для `page=0` и не описывает HTTP-статусы/ошибки. Поэтому результат нельзя
классифицировать как подтверждённый дефект API.

## Шаги и результаты

1. Отправить `GET {BASE_URL}/1.0/regions?page=0`.
2. **Ожидание characterization-теста:** HTTP 200, тело успешного ответа.
3. **Факт агентского прогона:** HTTP 500.

Ожидание отражает тестовый сценарий и не подтверждено контрактом.

## Evidence

Финальный прогон только `agents-test/func/`: 65 collected, 51 passed,
12 failed, 2 xfailed. Параметризованный case `page=0` упал в
`test_page_below_minimum` на сравнении `status_code == 200`.

## Связанный тест

`agents-test/func/test_characterization.py::TestRegionsCharacterization::test_page_below_minimum`

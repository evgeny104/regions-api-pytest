# Наблюдение: пустой `q` приводит к HTTP 500

**Классификация:** неопределённость контракта / неподтверждённое
characterization-ожидание\
**Severity:** не определена\
**Priority:** не определён\
**Component:** `GET /1.0/regions`, параметр `q`\
**Env:** `{BASE_URL}`; Windows, Python 3.14.10, pytest 9.1.1\
**Reporter:** regions-api-bug-reporter\
**Date:** 2026-11-03

## Наблюдение

Запрос с пустой строкой `q` завершился HTTP 500. Characterization-тест ожидал
HTTP 200 и объект ошибки в теле ответа.

## Контракт и ограничение

`tz-extracted.txt`, стр. 1, указывает минимальную длину `q`, но число заменено
NUL-символом. Контракт также не задаёт HTTP-статус или формат ошибки для
короткой строки. Нельзя подтвердить ни ожидание теста, ни конкретный дефект API.

## Шаги и результаты

1. Отправить `GET {BASE_URL}/1.0/regions?q=`.
2. **Ожидание characterization-теста:** HTTP 200 и непустой объект `error`.
3. **Факт агентского прогона:** HTTP 500.

## Evidence

Финальный прогон только `agents-test/func/`: 65 collected, 51 passed,
12 failed, 2 xfailed. Параметр `q=''` упал в
`test_q_minimum_and_blank_values` на ожидании HTTP 200.

## Связанный тест

`agents-test/func/test_characterization.py::TestRegionsCharacterization::test_q_minimum_and_blank_values`

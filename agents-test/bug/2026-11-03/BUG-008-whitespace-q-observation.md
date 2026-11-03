# Наблюдение: пробельный `q` возвращает пустую успешную выдачу

**Классификация:** неподтверждённое characterization-ожидание; нарушение
контракта не установлено\
**Severity:** не определена\
**Priority:** не определён\
**Component:** `GET /1.0/regions`, параметр `q`\
**Env:** `{BASE_URL}`; Windows, Python 3.14.10, pytest 9.1.1\
**Reporter:** regions-api-bug-reporter\
**Date:** 2026-11-03

## Наблюдение

Запрос с `q`, состоящим из трёх пробелов, вернул HTTP 200 и пустой список
результатов. Characterization-тест ожидал тело ошибки о минимальной длине
параметра.

## Контракт и ограничение

`tz-extracted.txt`, стр. 1, содержит минимальную длину `q`, но число в
извлечённом тексте заменено NUL-символом. Реакция на пробельную строку,
HTTP-статус и формат ошибки контрактом не заданы. Ожидание теста не доказывает
дефект API.

## Шаги и результаты

1. Отправить `GET {BASE_URL}/1.0/regions?q=%20%20%20`.
2. **Ожидание characterization-теста:** HTTP 200 и объект ошибки о длине `q`.
3. **Факт агентского прогона:** HTTP 200, `total=22`, `items=[]`.

## Evidence

Финальный прогон только `agents-test/func/`: 65 collected, 51 passed,
12 failed, 2 xfailed. Case `q='   '` упал в
`test_q_minimum_and_blank_values` при проверке наличия `error`.

## Связанный тест

`agents-test/func/test_characterization.py::TestRegionsCharacterization::test_q_minimum_and_blank_values`

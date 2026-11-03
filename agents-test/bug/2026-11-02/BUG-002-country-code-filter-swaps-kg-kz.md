# BUG-002 — Фильтр country_code возвращает регионы другой страны для kg и kz

**Severity:** Не определена
**Priority:** Не определён
**Component:** `GET /1.0/regions` — фильтр `country_code`
**Env:** `{BASE_URL}`
**Reporter:** Не указан
**Date:** 2026-11-02

## Описание

При фильтрации по `country_code=kg` ответ содержит элементы с `country.code=kz`. При запросе с
`country_code=kz` наблюдается обратное: в ответе есть элементы с `country.code=kg`. Фильтр по этим
двум кодам возвращает регионы, помеченные кодом другой страны.

## Нарушенное требование

В `tz.pdf`, стр. 2, параметр `country_code` описан как код страны для фильтрации; допустимые
значения включают `kg` и `kz`. Из назначения фильтра следует, что код страны каждого возвращённого
элемента должен совпадать с запрошенным кодом.

## Воспроизведение

1. Отправить `GET {BASE_URL}?country_code=kg`.
2. Проверить `country.code` у каждого объекта в `items`.
3. Повторить запрос с `GET {BASE_URL}?country_code=kz` и проверить те же поля.

## Ожидаемый результат

Оба запроса завершаются статусом `200`. Для первого запроса каждый элемент имеет
`country.code == "kg"`; для второго — `country.code == "kz"`.

## Фактический результат

По результатам полного прогона от 2026-11-02:

- для `country_code=kg` проверка получила `country.code == "kz"`;
- для `country_code=kz` проверка получила `country.code == "kg"`.

## Evidence

В журнале pytest зафиксированы проверки `assert 'kz' == 'kg'` для `country_code=kg` и
`assert 'kg' == 'kz'` для `country_code=kz`. Оба сценария также воспроизводятся в комбинированном
тесте при `page_size=5`, `10` и `15`.

## Связанные регрессионные тесты

- `tests/func/test_country_code.py::TestRegionsCountryCode::test_country_code_valid_values`
- `tests/func/test_combined.py::TestRegionsCombinedValidParams::test_country_and_pagination_together`

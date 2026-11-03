# Фильтр `country_code` возвращает смешанные страны для `kg` и `kz`

**Классификация:** подтверждённое нарушение контракта по текущему прогону
агентских тестов\
**Severity:** не определена\
**Priority:** не определён\
**Component:** `GET /1.0/regions`, фильтр `country_code`\
**Env:** `{BASE_URL}`; Windows, Python 3.14.10, pytest 9.1.1\
**Reporter:** regions-api-bug-reporter\
**Date:** 2026-11-03

## Описание

В свежем прогоне `agents-test/func/` фильтры `country_code=kg` и
`country_code=kz` возвращали одинаковую смешанную выдачу. В ней были регионы
обеих стран, поэтому проверка принадлежности каждого item запрошенному коду
падала. Наблюдение подтверждено в прямых тестах фильтра и его комбинациях с
пагинацией.

## Нарушенное требование

`tz-extracted.txt`, стр. 2, строка параметра `country_code`: параметр задаёт
код страны для фильтрации и принимает `ru`, `kg`, `kz`, `cz`. При запросе с
одним из этих кодов выдача должна соответствовать запрошенной стране.

## Шаги воспроизведения

1. Отправить `GET {BASE_URL}/1.0/regions?country_code=kg`.
2. Проверить, что у каждого объекта `items[]` поле `country.code` равно `kg`.
3. Повторить для `country_code=kz`.
4. Повторить с `page=1&page_size=5`, `10` и `15`.

## Expected

Для каждого запроса все элементы выдачи имеют `country.code`, равный
переданному `country_code`.

## Actual

Текущий агентский прогон зафиксировал для обоих прямых запросов HTTP 200,
`total=22` и шесть кодов в одинаковом порядке: `kz, kz, kz, kg, kg, kz`.
В параметризованных комбинированных сценариях `kg/kz × page_size=5/10/15`
assertion `all(item["country"]["code"] == expected_country ...)` также упал.
Для `page_size=5` наблюдались коды `kz, kz, kz, kg, kg`; для размеров `10/15`
— `kz, kz, kz, kg, kg, kz`.

## Evidence

Финальный запуск только `agents-test/func/`: 65 collected, 51 passed,
12 failed, 2 xfailed. Прямые strict XFAIL-сценарии для `kg` и `kz` были
повторены с раскрытием ответа; оба падения произошли на assertion однородности
`country.code`. Также упали шесть параметризованных сценариев
`test_characterization.py::TestRegionsCharacterization::test_country_filter_combined_with_page_size`.

## Регрессионные тесты

- `agents-test/func/test_country_code_contract.py::`
  `TestRegionsCountryCodeContract::test_country_code_filters_to_requested_country`
- `agents-test/func/test_characterization.py::TestRegionsCharacterization::test_country_filter_combined_with_page_size`

Тесты проверяют API через общие Pydantic-валидирующие fixtures. Причина дефекта
по имеющимся данным не установлена.

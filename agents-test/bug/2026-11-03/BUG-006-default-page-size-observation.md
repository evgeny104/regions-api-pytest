# Наблюдение: размер страницы по умолчанию равен 10 элементам

**Классификация:** неподтверждённое characterization-ожидание; нарушение
контракта не установлено\
**Severity:** не определена\
**Priority:** не определён\
**Component:** `GET /1.0/regions`, параметр `page_size`\
**Env:** `{BASE_URL}`; Windows, Python 3.14.10, pytest 9.1.1\
**Reporter:** regions-api-bug-reporter\
**Date:** 2026-11-03

## Наблюдение

Запрос без `page_size` вернул 10 элементов. Агентский characterization-тест
ожидал 15 элементов.

## Контракт и ограничение

В `tz-extracted.txt`, стр. 2, значение по умолчанию `page_size` заменено
NUL-символом. Требование о default=15 недоступно для проверки по извлечённому
контракту, поэтому это наблюдение само по себе не подтверждает дефект API.

## Шаги и результаты

1. Отправить `GET {BASE_URL}/1.0/regions` без query-параметров.
2. **Ожидание characterization-теста:** HTTP 200 и 15 элементов `items`.
3. **Факт агентского прогона:** ответ успешный; в `items` 10 элементов.

## Evidence

Финальный прогон только `agents-test/func/`: 65 collected, 51 passed,
12 failed, 2 xfailed. Case `characterization default page_size=15` упал на
`len(data["items"]) == 15`.

## Связанный тест

`agents-test/func/test_characterization.py::TestRegionsCharacterization::test_page_size_default`

# BUG-001 — Пагинация возвращает дубликаты между страницами

**Severity:** Major
**Priority:** High
**Component:** `GET /1.0/regions` — pagination
**Env:** `{BASE_URL}` (значение см. `src/config/url.py`)
**Reporter:** evgeny104
**Date:** 2026-10-28

## Описание

При запросах разных страниц API повторяет элементы по `id`. На последней странице
также наблюдалось переполнение: API возвращал полную страницу размером
`page_size` с элементами предыдущих страниц вместо реального остатка
`total − (last_page − 1) × page_size`.

По ТЗ контракт пагинации стандартный: `page` — порядковый номер страницы,
`page_size` — элементов на странице, `total` — общее количество регионов в базе
(пример в ТЗ: `total == 22`). Из этого следует, что страница
`N = ceil(total / page_size)` содержит ровно `total − (N − 1) × page_size` элементов.

## Воспроизведение

### Case A — `page_size=5`

**URL:**
```
GET {BASE_URL}?page=5&page_size=5
```

**Expected:** `len(items) == 2` (`22 − 4 × 5 = 2`)
**Actual:** `len(items) == 5`

**Фактический ответ (`items`):**
```json
[
  {"id": 92, "name": "Прага",            "code": "praha",  "country": {"name": "Чехия",    "code": "cz"}},
  {"id": 38, "name": "Санкт-Петербург",  "code": "spb",    "country": {"name": "Россия",   "code": "ru"}},
  {"id": 3,  "name": "Томск",            "code": "tomsk",  "country": {"name": "Россия",   "code": "ru"}},
  {"id": 91, "name": "Усть-Каменогорск", "code": "ustkam", "country": {"name": "Казахстан","code": "kz"}},
  {"id": 17, "name": "Уфа",              "code": "ufa",    "country": {"name": "Россия",   "code": "ru"}}
]
```

Все пять `id` на странице 5 уже присутствовали в выборке страниц 1–4 → **дубликаты**.

### Case B — `page_size=10`

**URL:**
```
GET {BASE_URL}?page=3&page_size=10
```

**Expected:** `len(items) == 2` (`22 − 2 × 10 = 2`)
**Actual:** `len(items) == 3`

**Фактический ответ (`items`):**
```json
[
  {"id": 3,  "name": "Томск",            "code": "tomsk",  "country": {"name": "Россия",    "code": "ru"}},
  {"id": 91, "name": "Усть-Каменогорск", "code": "ustkam", "country": {"name": "Казахстан", "code": "kz"}},
  {"id": 17, "name": "Уфа",              "code": "ufa",    "country": {"name": "Россия",    "code": "ru"}}
]
```

Один лишний элемент сверх реального остатка — такой же тип бага, с меньшей амплитудой.

## Контрольный кейс (без бага)

**URL:**
```
GET {BASE_URL}?page=2&page_size=15
```

**Expected:** `22 − 1 × 15 = 7`
**Actual:** 7 ✅

При `page_size`, близком к `total`, остаток велик и баг не проявляется — отсюда и то,
что он не ловился «обычным» тестом на последнюю страницу.

### Case C — пересечение страниц 2 и 3 (`page_size=5`)

**Дата наблюдения:** 2026-11-03.

**Запросы:**
```
GET {BASE_URL}?page=2&page_size=5
GET {BASE_URL}?page=3&page_size=5
```

**Expected:** множества `id` на разных страницах не пересекаются. Это следует
из значения `page` как порядкового номера страницы; см. `tz-extracted.txt`,
стр. 2, таблица query-параметров `page`.

**Actual:** оба ответа прошли проверки HTTP-статуса `200` и непустых `items`,
но проверка непересечения завершилась ошибкой: пересечение множеств `id` — `{26}`.
Полные тела ответов для этого прогона не сохранены.

**Evidence:** пользовательский вывод pytest от 2026-11-03 для
`agents-test/func/test_pagination_contract.py::TestRegionsPaginationContract::test_page_number_selects_a_different_page`;
ошибка на assertion `ids_a.isdisjoint(ids_b)`.

### Case D — перекрытие соседних страниц в полном прогоне

**Дата наблюдения:** 2026-11-03.

В полном прогоне `pytest tests/func agents-test/func` проверка соседних страниц
завершилась тремя ошибками на assertion непересечения ID:

- `page=1`/`page=2`, `page_size=5`: пересечение `{114}`;
- `page=1`/`page=2`, `page_size=10`: пересечение `{32}`;
- `country_code=ru`, `page=1`/`page=2`, `page_size=5`: пересечение `{32}`.

**Evidence:** вывод pytest от 2026-11-03 для
`tests/func/test_pagination.py::TestRegionsPagination::test_pages_are_disjoint_and_total_stable`.
В этом прогоне собрано 76 тестов: 58 passed, 12 xfailed, 6 failed.
Отдельный авторский прогон после восстановления assertion завершился ожидаемым
`XFAIL` по текущему регрессионному тесту; подробные тела ответов не сохранены.

## Инварианты, которые нарушены

1. `len(items_on_last_page) == total − (last_page − 1) × page_size`.
2. **Уникальность `id`** в рамках полной выборки по страницам: регионы `[92, 38, 3, 91, 17]` отдаются дважды.
3. Косвенно — `sum(len(items_pageN)) == total`: сейчас сумма > `total` (24 вместо 22
   при `page_size=5`, 23 вместо 22 при `page_size=10`).

## Предполагаемая причина

**Гипотеза:** возможно, на бэкенде неверно вычисляется `OFFSET`/`LIMIT`. Когда
`(page − 1) × page_size + page_size` выходит за реальное число строк, выборка «добивается»
до размера страницы и повторно выбирает элементы. Возможные причины — отсутствие
корректного `ORDER BY` или ошибочный циклический индекс; это не подтверждено.

## Impact

- Клиенты, которые собирают полный список регионов постранично, получают
  **дубликаты** и завышенное фактическое число записей.
- Любая дедупликация на клиенте маскирует симптом, но не чинит контракт.

## Регрессионный автотест

Поведение зафиксировано в исходном тесте
`tests/func/test_pagination.py::TestRegionsPagination::test_last_page_returns_remainder`
и новом тесте
`agents-test/func/test_pagination_contract.py::TestRegionsPaginationContract::test_page_number_selects_a_different_page`.

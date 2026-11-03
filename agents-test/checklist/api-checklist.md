# Чек-лист требований публичного Regions API

Источник требований: `tz-extracted.txt`. Проверки, ожидаемое поведение которых
контракт не задаёт, вынесены в неопределённости и не считаются обязательным
покрытием.

## Применённые техники тест-дизайна

- **Классы эквивалентности:** для `country_code` проверяются все четыре явно
  перечисленных допустимых кода (`ru`, `kg`, `kz`, `cz`). Любые другие значения
  не образуют контрактный негативный класс: реакция API не описана.
- **Граничные значения:** минимумы и значения по умолчанию `q`, `page`,
  `page_size` заменены NUL-символами. Границы нельзя восстановить из доступного
  текста, поэтому значения старых тестов не принимаются за требования.
- **Позитивные проверки:** пример поиска `q=рск`, четыре значения фильтра и
  примеры параметров пагинации проверяются там, где указан наблюдаемый результат.
- **Негативные проверки:** контракт не задаёт поведение, коды статуса или поля
  ошибки для недопустимых значений; такие случаи не включены как контрактные.
- **Комбинации / таблица решений:** при наличии `q` остальные query-параметры
  игнорируются. Без `q` отдельно применяются требования `country_code`, `page`
  и `page_size`; ожидаемое поведение их комбинаций не расширяется сверх текста.
- **Структура и семантика ответа:** поля из JSON-примера сопоставляются отдельно
  со схемой и примерными значениями. Переходы состояний неприменимы: API описан
  только как чтение списка.

## Правила измерения покрытия

Чек-лист — это план обязательных контрактных проверок и карта их трассируемости,
а не подсчёт количества pytest-функций или строк `assert`.

- Единица покрытия — атомарный сценарий с собственным ID в плане ниже; набор
  параметров считается несколькими сценариями, если параметры проверяют разные
  классы эквивалентности или условия.
- Статус «Покрыто» допустим, только если assertion проверяет ожидаемое поведение
  этого сценария. Проверка статуса ответа, успешной схемы или непустого списка
  сама по себе не покрывает семантический assertion.
- `tests/func/` и `agents-test/func/` учитываются раздельно. Пользовательские
  сценарии — сравнительный ориентир; они не заменяют отсутствующий агентский
  тест. Неоднозначные или неподтверждённые контрактом ожидания помечаются как
  дополнительные пользовательские проверки, а не копируются в обязательный
  агентский план.
- Полное покрытие означает, что каждый применимый сценарий плана имеет
  агентский тест и нужный assertion. Для частичного покрытия обязательно
  назвать отсутствующий assertion или оракул; непроверяемый сценарий требует
  объективной причины из контракта/данных.
- Количество собранных параметризованных case-ов и число assertion-выражений
  записываются только как диагностические показатели прогона. Они не являются
  оценкой покрытия без трассировки к сценариям ниже.

## План контрактных сценариев

Идентификаторы сохраняют родительский ID требования. Под-ID выделяют атомарные
классы данных и независимые ожидаемые результаты, не добавляя новых требований.

### API-001a — Структурная/типовая валидация
- Проверка: Ответ и вложенные элементы соответствуют JSON-схеме и точным wire-типам.
- Тест и assertion: Общая строгая Pydantic-валидация на каждом вызове;
  `test_response_contract.py::test_documented_region_fields_and_values` дополнительно проверяет `total` — int, `items` —
  list.

### API-004a — Пример данных
- Проверка: Для объекта Новосибирска `name == "Новосибирск"`.
- Тест и assertion: `test_response_contract.py::test_documented_region_fields_and_values`: найти объект и сравнить
  `name`.

### API-005a — Пример данных
- Проверка: У Новосибирска `code == "novosibirsk"`.
- Тест и assertion: Тот же тест: сравнить `code`.

### API-006a — Структура + пример данных
- Проверка: `country` — вложенный объект; примерные `name == "Россия"`, `code == "ru"`.
- Тест и assertion: Тот же тест: сравнить обе вложенные строки; строгая модель проверяет wire-типы.

### API-002a — Сравнение последовательных запросов
- Проверка: При изменении страницы `total` остаётся одинаковым и больше числа элементов страницы.
- Тест и assertion: `test_response_contract.py::test_total_stays_stable_when_page_changes`: равенство `total`;
  `test_pagination_contract.py::test_page_number_changes_selected_result`: `total > len(items)`.

### API-002b — Вариация размера страницы
- Проверка: Проверить, как `total` ведёт себя при `page_size=5/10/15`. Семантика общего числа базы говорит в пользу
  инвариантности, но `10/15` затёрты в таблице параметров. До восстановления контрактных значений это characterization, а
  не безусловный conformance verdict.
- Тест и assertion: `test_response_contract.py::test_total_stays_stable_across_page_sizes` сравнивает значения для
  5/10/15; assertion присутствует и результат отражает наблюдение, но покрытие отмечать как
  characterization/ограниченное. Пользовательский аналог:
  `test_page_size.py::test_total_is_stable_across_page_sizes_and_country_filter`.

### API-002c — Фильтр и семантика общего `total`
- Проверка: Сравнить `total` до/после `country_code=ru`. Текст буквально называет `total` количеством записей базы, но не
  разъясняет, считается ли оно до/после фильтрации. Поэтому это characterization и открытый контрактный вопрос, не
  conformance oracle.
- Тест и assertion: `test_response_contract.py::test_total_with_country_filter_characterization` сравнивает baseline и
  filtered total, с assertion явно помеченным characterization. Пользовательский аналог:
  `test_page_size.py::test_total_is_stable_across_page_sizes_and_country_filter`.

### API-003a — Уникальность в странице
- Проверка: Внутри одной страницы каждый `id` встречается один раз.
- Тест и assertion: `test_response_contract.py::test_ids_are_unique_within_each_sampled_page`: длина списка ID равна
  длине множества.

### API-003b — Consistency map ID → видимый кортеж
- Проверка: При обходе страниц фиксировать `id -> (name, code, country.name, country.code)` и отмечать, если один ID
  меняет видимый кортеж. Одинаковый кортеж может принадлежать разным реальным регионам, поэтому такой тест проверяет
  только consistency наблюдаемого представления, не глобальную уникальность ID.
- Тест и assertion: `test_response_contract.py::test_ids_keep_the_same_entity_across_pages` проверяет неизменность
  кортежа для встреченного ID. Это characterization consistency; API-003 остаётся частично покрытым, пока нет
  независимого идентификатора сущности/полного оракула уникальности.

### API-007a — Пример + содержимое результата
- Проверка: При `q=рск` каждый результат содержит `рск`; присутствуют три названия из примера.
- Тест и assertion: `test_q_contract.py::test_q_matches_requested_substring_and_examples`: `all(...)` и включение трёх
  имен в множество.

### API-008a — Эквивалентные входы
- Проверка: Нижний/верхний регистр `q=рск` даёт одинаковый набор ID.
- Тест и assertion: `test_q_contract.py::test_q_results_do_not_depend_on_letter_case`: множества ID равны.

### API-009a — Таблица решений/комбинации
- Проверка: Каждый дополнительный параметр отдельно и все вместе при наличии `q` не меняют выдачу.
- Тест и assertion: `test_q_contract.py::test_q_ignores_other_query_parameters`: параметризация `country_code`, `page`,
  `page_size`, комбинация; сравнить ID и `total` с baseline.

### API-010a–d — Классы эквивалентности
- Проверка: Каждое из четырёх перечисленных значений (`ru`, `kg`, `kz`, `cz`) фильтрует все элементы на свой код.
- Тест и assertion: `test_country_code_contract.py::test_country_code_filters_to_requested_country`: четыре параметра и
  `all(item["country"]["code"] == expected_country ...)`; текущие kg/kz failures описаны агентским BUG-004.

### API-011a — Default / полный обход страниц
- Проверка: Без `country_code` выборка включает все четыре страны, перечисленные в контракте.
- Тест и assertion: `test_country_code_contract.py::test_default_country_code_includes_documented_countries`: объединить
  коды страниц и проверить включение `ru/kg/kz/cz`; полный справочник не задан.

### API-012a — Сравнение соседних наблюдаемых страниц
- Проверка: Примерные `page=2` и `page=3` при `page_size=5` выбирают разные наборы; порядок/непересечение не выводятся.
- Тест и assertion: `test_pagination_contract.py::test_page_number_changes_selected_result`: проверить `ids_page2 !=
  ids_page3`.

### API-013a — Пример граничного размера страницы
- Проверка: Для указанного примера `page_size=5` полная страница содержит 5 элементов.
- Тест и assertion: `test_pagination_contract.py::test_documented_page_size_controls_full_page`: `len(items) == 5`.

### API-014a — Проверка учебного примера
- Проверка: В отдельном учебном примере ожидается `total == 22`; это не обобщается на контрактную семантику.
- Тест и assertion: `test_response_contract.py::test_total_matches_assignment_example`: `total == 22`.


## Сопоставление со всеми пользовательскими тест-сценариями

Ниже перечислены все тестовые методы `tests/func/` и число статически видимых
parameter cases (без выполнения pytest). Классификация «контракт» означает, что
проверяемая часть поддержана `tz-extracted.txt`; остальные assertions того же
метода могут оставаться characterization. Неподтверждённые ожидания не становятся
дефектом только из-за падения теста. Указанное число — число вызовов pytest по
декораторам/явным циклам, не число независимых требований.

### `test_page.py::test_page_min_boundary_valid` (1 case)
- Контрактная связь: `page=1` / минимум и валидность — characterization: значение минимума затёрто.
- Агентский паритет: `test_characterization.py::test_page_minimum_and_default` включает этот вариант; characterization.

### `test_page.py::test_page_default_value` (1 case)
- Контрактная связь: default `page=1` — characterization: default затёрт.
- Агентский паритет: `test_characterization.py::test_page_minimum_and_default` включает этот вариант; characterization.

### `test_page.py::test_page_valid_positive` (2 cases)
- Контрактная связь: Примеры `page=2/3`: каждый запрос успешен и непуст — наблюдаемое поведение вне точного contract
  oracle; выбранные номера приводятся как примеры.
- Агентский паритет: `test_pagination_contract.py::test_page_number_changes_selected_result` сравнивает наборы для page
  2/3; не дублирует успешный непустой результат каждого кейса как самостоятельный критерий.

### `test_page.py::test_page_below_min_invalid` (2 cases)
- Контрактная связь: `page=0/-1`, HTTP/error expectations — characterization; минимум и формат ошибки затёрты/не заданы.
- Агентский паритет: `test_characterization.py::test_page_below_minimum`; characterization.

### `test_page.py::test_page_non_integer_invalid` (2 cases)
- Контрактная связь: Строковые дробь/нечисло и ошибка — characterization; не описано контрактом.
- Агентский паритет: `test_characterization.py::test_page_non_integer`; characterization.

### `test_page.py::test_page_above_total` (1 case)
- Контрактная связь: Большая страница допускает выбранную автором альтернативу error либо пустые items —
  characterization, контракт не задаёт.
- Агентский паритет: `test_characterization.py::test_page_above_total`; characterization с тем же набором альтернатив.

### `test_page_size.py::test_total_is_stable_across_page_sizes_and_country_filter` (1 case)
- Контрактная связь: Сравнение `total` для размеров и `ru` — API-002b/002c; `10/15` затёрты, влияние фильтра на `total`
  неоднозначно.
- Агентский паритет: `test_total_stays_stable_across_page_sizes` и `test_total_with_country_filter_characterization`
  покрывают эти срезы как characterization/ограниченные оракулы.

### `test_page_size.py::test_page_size_valid_values` (3 cases)
- Контрактная связь: `5/10/15`: только `5` читаемо дано как пример (API-013); `10/15` — characterization до
  восстановления текста.
- Агентский паритет: `test_pagination_contract.py::test_documented_page_size_controls_full_page` для `5`;
  `test_characterization.py::test_page_size_values` дополнительно фиксирует 5/10/15, где 10/15 characterization.

### `test_page_size.py::test_page_size_default_value` (1 case)
- Контрактная связь: default `15` и точный размер — characterization: default затёрт.
- Агентский паритет: `test_characterization.py::test_page_size_default`; characterization.

### `test_page_size.py::test_page_size_undocumented_invalid` (3 cases)
- Контрактная связь: `1/20/100` как invalid и формат ошибки — characterization; множество значений частично затёрто,
  error contract отсутствует.
- Агентский паритет: `test_characterization.py::test_page_size_non_positive_or_undocumented` включает 1/20/100;
  characterization.

### `test_page_size.py::test_page_size_non_positive_invalid` (3 cases)
- Контрактная связь: `0/-1/-5` и error — characterization, границы/error не заданы читаемым контрактом.
- Агентский паритет: `test_characterization.py::test_page_size_non_positive_or_undocumented`; characterization.

### `test_page_size.py::test_page_size_non_integer_invalid` (2 cases)
- Контрактная связь: `abc/5.5` и error — characterization; типовая валидация параметра не описана.
- Агентский паритет: `test_characterization.py::test_page_size_non_integer`; characterization.

### `test_pagination.py::test_pages_are_disjoint_and_total_stable` (3 cases)
- Контрактная связь: Стабильность `total` относится API-002; непересечение страниц не обещано контрактом. Размер `10` и
  combination with `ru` — characterization.
- Агентский паритет: Агент проверяет стабильность total для page 1/2, size 5; разницу выдач page 2/3. Не должно требовать
  disjointness без уточнения контракта.

### `test_pagination.py::test_last_page_returns_remainder` (3 cases)
- Контрактная связь: Ожидаемое число элементов на последней странице — characterization: контракт не задаёт поведение
  последней страницы и remainder.
- Агентский паритет: `test_characterization.py::test_last_page_contains_expected_remainder` с page_size 5/10/15;
  characterization.

### `test_country_code.py::test_country_code_valid_values` (4 cases)
- Контрактная связь: Фильтр и все перечисленные допустимые коды — API-010; тестовые ожидания пользовательской suite
  приведены как read-only reference, без ссылки на исторические баг-репорты.
- Агентский паритет: `test_country_code_contract.py::test_country_code_filters_to_requested_country`: все четыре значения
  и сравнение фактических country codes; kg/kz strict xfail связаны с актуальным агентским BUG-004.

### `test_country_code.py::test_country_code_default` (1 case)
- Контрактная связь: Default отображает регионы из всех стран (API-011); непустой ответ недостаточен для полного
  утверждения.
- Агентский паритет: `test_country_code_contract.py::test_default_country_code_includes_documented_countries`: проверяет
  включение четырёх упомянутых кодов, не равенство списка.

### `test_country_code.py::test_country_code_undocumented_invalid` (3 cases)
- Контрактная связь: `us/de/xx` и ошибка — characterization; контракт не описывает ошибочное значение/ошибку.
- Агентский паритет: `test_characterization.py::test_undocumented_country_code_values` включает эти коды;
  characterization.

### `test_country_code.py::test_country_code_empty_invalid` (1 case)
- Контрактная связь: Пустой код и ошибка — characterization.
- Агентский паритет: `test_characterization.py::test_undocumented_country_code_values`; characterization.

### `test_country_code.py::test_country_code_case_sensitive_invalid` (2 cases)
- Контрактная связь: `RU/Ru` и ошибка — characterization; регистр кодов отдельно не задан.
- Агентский паритет: `test_characterization.py::test_undocumented_country_code_values`; characterization.

### `test_combined.py::test_country_and_pagination_together` (12 cases)
- Контрактная связь: Комбинация country/page/page_size: фильтр поддержан API-010; `page_size=5` дан примером; page=1,
  размеры 10/15 и interaction — characterization до читаемого контракта.
- Агентский паритет: `test_characterization.py::test_country_filter_combined_with_page_size` параметризует все 4 кода × 3
  размера; characterization комбинаций, при этом `country_code` semantics ссылается на API-010.

### `test_q.py::test_param_q` (4 cases)
- Контрактная связь: Fuzzy substring, case-insensitivity и пример `q=Новосибирск` поддержаны (API-007/008); текущее
  assertion всегда ищет `нов`, поэтому только параметры, содержащие эту подстроку, имеют meaningful assertion.
- Агентский паритет: Агент проверяет конкретный контрактный `рск` и равенство результатов для `рск/РСК`. Это сильнее и
  точнее для документированного примера; нельзя считать пользовательские кейсы целиком покрытыми.

### `test_q.py::test_q_min_length_invalid` (4 cases)
- Контрактная связь: Минимум 3 и точное error body/message — characterization: длина затёрта, формат error отсутствует.
- Агентский паритет: `test_characterization.py::test_q_minimum_and_blank_values` включает короткие/пустые значения;
  characterization.

### `test_q.py::test_q_ignores_other_params_fuzzy` (4 cases)
- Контрактная связь: Игнорирование прочих параметров поддержано API-009, но эти assertions фиксируют конкретное наличие
  Новосибирска/более одного элемента; некоторые значения и точные выдачи не подтверждены.
- Агентский паритет: `test_q_contract.py::test_q_ignores_other_query_parameters` сравнивает ID-set и total для documented
  `cz`, added `us`, page, page_size и комбинации; API-009 покрыт этими решениями таблицы.

### `test_q.py::test_q_ignores_other_params_exact` (3 cases)
- Контрактная связь: Приоритет `q` поддержан API-009; exact-query combinations — characterization сверх явно показанного
  поведения, где поддержка самого ignore rule остаётся контрактной.
- Агентский паритет: `test_q_contract.py::test_q_ignores_other_query_parameters` проверяет общий ignore rule и комбинации
  при `q=рск`; не заявлять exact Новосибирск как отдельный агентский case.


**Итого по статической инвентаризации:** 24 метода, 66 вызовов pytest в
`tests/func/`; 26 методов в 5 файлах и 65 вызовов pytest в `agents-test/func/`.
Из них 44 cases относятся к characterization-классу и 21 — к основным
контрактным/учебным тестам (включая strict xfail); characterization assertions
полезны для сравнения поведения, но не увеличивают доказанное контрактное
покрытие. План содержит 20 атомарных сценариев: API-002b и API-002c имеют
characterization assertions, API-003b проверяет лишь консистентность видимого
кортежа и не доказывает уникальность ID разных сущностей; API-003 остаётся
частичным. API-011 частичен: equality нельзя установить без полного country
inventory.

## Результат последнего агентского прогона

Отдельно от статуса покрытия: последняя зафиксированная команда для
`agents-test/func/` собрала 65 cases: **51 passed, 12 failed, 2 xfailed**.
Статическая инвентаризация кода: 26 test-методов в пяти файлах и 108
выражений `assert`; это диагностические числа, не метрика покрытия.
Это результат выполнения, а не показатель полноты/качества трассируемости.
Причины двенадцати падений требуют классификации по логам конкретного прогона;
не превращать падение characterization-теста в подтверждённое нарушение
контракта. Статус каждого сценария выше определяется только требованиями и
assertions, не итогом pytest.

Параметризованные case-ы внутри метода не следует считать покрытыми по имени
метода целиком: reviewer сверяет каждый указанный вариант и соответствующий
expected assertion. Если метод покрывает лишь часть перечисленных значений,
фиксируется частичное покрытие с перечислением пропусков.

## Матрица требований и покрытия

Покрытие пользовательской suite `tests/func/` и независимой агентской suite
`agents-test/func/` указано раздельно в каждой строке. Корневой `conftest.py`
применяет к ответам обеих suites общие строгие Pydantic-модели; модель проверяет
wire-типы без приведения несовпадающих JSON-типов.

### API-001 — `GET /1.0/regions`, форма ответа
- **Требование и сценарий:** Проверить envelope и каждый элемент: `total`, `items`, `id`, `name`, `code`, `country.name`,
  `country.code`.
- **Ожидаемый результат:** Wire-типы и вложенная структура точно соответствуют Pydantic-схеме для JSON-ответа.
- **Источник:** Стр. 1, JSON-пример, строки 1–14
- **Покрытие:** Покрыто
- **Тесты и заметка:** **Пользовательские:** общая fixture в корневом `conftest.py` валидирует все ответы через строгие
  `RegionResponse`/`RegionErrorResponse`; например,
  `tests/func/test_page.py::TestRegionsPage::test_page_min_boundary_valid`. **Агентские:** та же строгая валидация;
  `agents-test/func/test_response_contract.py::TestRegionsResponseContract::test_documented_region_fields_and_values`
  явно проверяет `total` и `items`.

### API-002 — `GET /1.0/regions`, семантика `total`
- **Требование и сценарий:** `total` описан как общее число регионов в базе. Проверять при смене page, page_size и
  country filter; сравнение размеров и фильтра уже есть как characterization (API-002b/c), не нормативный вывод.
- **Ожидаемый результат:** Буквальное прочтение требует общего DB-total; контракт отдельно не говорит, считается ли total
  до/после фильтрации. Число 22 из учебного примера не заменяет comparative coverage.
- **Источник:** Стр. 1, поле `total` и комментарий к строке 2
- **Покрытие:** Частично: page покрыт по контракту, page_size/filter — characterization
- **Тесты и заметка:** **Пользовательские:**
  `tests/func/test_page_size.py::TestRegionsPageSize::test_total_is_stable_across_page_sizes_and_country_filter`
  сравнивает 5/10/15 и `country_code=ru`;
  `tests/func/test_pagination.py::TestRegionsPagination::test_pages_are_disjoint_and_total_stable` сравнивает страницы.
  **Агентские:** `test_response_contract.py::test_total_stays_stable_when_page_changes` проверяет смену страницы;
  `test_total_stays_stable_across_page_sizes` сравнивает 5/10/15 как characterization;
  `test_total_with_country_filter_characterization` сравнивает baseline с `country_code=ru` как characterization.

### API-003 — `GET /1.0/regions`, уникальный `items[].id`
- **Требование и сценарий:** Поле `id` помечено как уникальный идентификатор региона. Проверить повторы в выдаче и
  конфликтующие ID разных сущностей при наличии независимого оракула сущности. Текущая tuple map проверяет лишь
  стабильность представления.
- **Ожидаемый результат:** Один ID у разных реальных сущностей — конфликт; повтор одного ID/tuple в ответах сам по себе
  не устанавливает collision, поскольку tuple может не идентифицировать сущность уникально. Wire-тип `id` — integer по
  примеру.
- **Источник:** Стр. 1, строка 5, комментарий к `id`
- **Покрытие:** Частично
- **Тесты и заметка:** **Пользовательские:** `tests/func/test_q.py::TestRegionsQ::test_param_q` проверяет повторы ID
  внутри поискового ответа; `test_pages_are_disjoint_and_total_stable` требует непересечения ID страниц, но это не
  эквивалентно глобальной уникальности. **Агентские:** `test_ids_are_unique_within_each_sampled_page` проверяет страницу;
  `test_ids_keep_the_same_entity_across_pages` проверяет только повтор видимого tuple для одного ID. Уникальность ID
  разных реальных сущностей не доказана без полного независимого оракула; API-003 остаётся partial.

### API-004 — `GET /1.0/regions`, `items[].name`
- **Требование и сценарий:** Проверить строковый `name` и примерное значение названия Новосибирска.
- **Ожидаемый результат:** Поле имеет wire-тип string; у объекта-примера `name == "Новосибирск"`.
- **Источник:** Стр. 1, строка 6 и комментарий к `name`
- **Покрытие:** Покрыто
- **Тесты и заметка:** **Пользовательские:** Pydantic проверяет string;
  `tests/func/test_q.py::TestRegionsQ::test_param_q` дополнительно проверяет подстроку `нов` в именах. **Агентские:**
  `agents-test/func/test_response_contract.py::TestRegionsResponseContract::test_documented_region_fields_and_values`
  находит пример и assert-ит точное имя `Новосибирск`; строгая Pydantic-модель проверяет wire-тип.

### API-005 — `GET /1.0/regions`, `items[].code`
- **Требование и сценарий:** Проверить строковый код региона и значение из JSON-примера.
- **Ожидаемый результат:** Поле имеет wire-тип string; у Новосибирска `code == "novosibirsk"`.
- **Источник:** Стр. 1, строка 7 и комментарий к `code`
- **Покрытие:** Покрыто
- **Тесты и заметка:** **Пользовательские:** только строгая Pydantic-валидация wire-типа. **Агентские:**
  `agents-test/func/test_response_contract.py::TestRegionsResponseContract::test_documented_region_fields_and_values`
  assert-ит `example["code"] == "novosibirsk"`; Pydantic проверяет string без coercion.

### API-006 — `GET /1.0/regions`, вложенный объект `country`
- **Требование и сценарий:** Проверить `country.name` и `country.code`, их wire-типы и примерную пару для Новосибирска.
- **Ожидаемый результат:** `country` — объект, оба поля string; пример: `Россия` / `ru`.
- **Источник:** Стр. 1, строки 8–10 и комментарии
- **Покрытие:** Покрыто
- **Тесты и заметка:** **Пользовательские:** Pydantic проверяет вложенную схему;
  `tests/func/test_country_code.py::test_country_code_valid_values` и
  `tests/func/test_combined.py::test_country_and_pagination_together` проверяют `country.code` для фильтра.
  **Агентские:**
  `agents-test/func/test_response_contract.py::TestRegionsResponseContract::test_documented_region_fields_and_values`
  assert-ит `country.name == "Россия"` и `country.code == "ru"`; строгая схема проверяет wire-типы.

### API-007 — `GET /1.0/regions`, fuzzy-поиск `q`
- **Требование и сценарий:** Для `q=рск` проверить substring-класс и все три перечисленных в контракте имени:
  Новосибирск, Магнитогорск, Орск.
- **Ожидаемый результат:** Все результаты содержат `рск`; все три примерных названия присутствуют.
- **Источник:** Стр. 1–2, описание `q` и сноска о fuzzy-поиске
- **Покрытие:** Покрыто
- **Тесты и заметка:** **Пользовательские:** `tests/func/test_q.py::TestRegionsQ::test_param_q` проверяет примеры на
  `нов`/`НОВ`/`ново`, но assert не использует фактический `q`. **Агентские:**
  `agents-test/func/test_q_contract.py::TestRegionsQContract::test_q_matches_requested_substring_and_examples` assert-ит
  подстроку `рск` у всех имён и наличие трёх контрактных названий.

### API-008 — `GET /1.0/regions`, регистр `q`
- **Требование и сценарий:** Сравнить один поисковый запрос в нижнем и верхнем регистре.
- **Ожидаемый результат:** Регистр не меняет набор результатов.
- **Источник:** Стр. 1, таблица параметров, строка `q`: «Регистр не имеет значения»
- **Покрытие:** Покрыто
- **Тесты и заметка:** **Пользовательские:** `tests/func/test_q.py::TestRegionsQ::test_param_q` отправляет `нов` и `НОВ`,
  но не сравнивает выборки. **Агентские:**
  `agents-test/func/test_q_contract.py::TestRegionsQContract::test_q_results_do_not_depend_on_letter_case` сравнивает
  множества `id` для `рск`/`РСК`.

### API-009 — `GET /1.0/regions`, приоритет `q`
- **Требование и сценарий:** Сравнить baseline с тем же `q` при добавлении `country_code`, `page`, `page_size` по
  отдельности и вместе.
- **Ожидаемый результат:** При наличии `q` дополнительные параметры игнорируются; набор регионов и `total` не меняются.
- **Источник:** Стр. 1–2, продолжение описания `q`: остальные параметры игнорируются
- **Покрытие:** Покрыто
- **Тесты и заметка:** **Пользовательские:** `tests/func/test_q.py::TestRegionsQ::test_q_ignores_other_params_fuzzy` и
  `test_q_ignores_other_params_exact` проверяют наличие Новосибирска/количество, но не полное равенство выдач.
  **Агентские:** `agents-test/func/test_q_contract.py::TestRegionsQContract::test_q_ignores_other_query_parameters`
  параметризует каждый параметр и их комбинацию, сравнивает множества `id` и `total` с baseline.

### API-010 — `GET /1.0/regions`, фильтр `country_code`
- **Требование и сценарий:** Эквивалентный класс допустимых значений: отдельно проверить `ru`, `kg`, `kz`, `cz`.
- **Ожидаемый результат:** Каждый item имеет `country.code`, равный переданному коду.
- **Источник:** Стр. 2, таблица параметров, строка `country_code`
- **Покрытие:** Покрыто; текущий дефект в kg/kz
- **Тесты и заметка:** **Пользовательские:**
  `tests/func/test_country_code.py::TestRegionsCountryCode::test_country_code_valid_values` проверяет все четыре кода;
  исторические пользовательские баг-ID в этой матрице не учитываются. **Агентские:**
  `agents-test/func/test_country_code_contract.py::`
  `TestRegionsCountryCodeContract::test_country_code_filters_to_requested_country`
  проверяет четыре класса; kg/kz помечены strict `xfail` с текущим агентским отчётом BUG-004. Нарушение повторно
  подтверждено также в characterization комбинациях.

### API-011 — `GET /1.0/regions`, `country_code` отсутствует
- **Требование и сценарий:** Default-класс: запрос без `country_code` должен отображать регионы из всех стран.
- **Ожидаемый результат:** Возвращаются регионы всех стран. Перечень `ru/kg/kz/cz` относится к допустимым значениям
  параметра, не доказывает, что база содержит только эти страны; equality с четырьмя кодами нельзя требовать.
- **Источник:** Стр. 2, строка `country_code`: «По умолчанию отображаются регионы из всех стран»
- **Покрытие:** Частично
- **Тесты и заметка:** **Пользовательские:**
  `tests/func/test_country_code.py::TestRegionsCountryCode::test_country_code_default` проверяет только успешный непустой
  ответ. **Агентские:** `test_country_code_contract.py::test_default_country_code_includes_documented_countries` обходит
  страницы и проверяет включение четырёх кодов, но не исключает иные. Даже equality не годится как оракул: контракт не
  утверждает, что допустимые фильтры исчерпывают страны базы. Для полного покрытия нужен источник полного country
  inventory либо уточнение контракта.

### API-012 — `GET /1.0/regions`, порядковый номер `page`
- **Требование и сценарий:** Сравнить ответы `page=2` и `page=3` при одном документированном `page_size=5`; границы и
  default `page` неизвестны.
- **Ожидаемый результат:** Изменение `page` меняет выбранный набор результатов; конкретные ID, порядок и непересечение
  контрактом не заданы.
- **Источник:** Стр. 2, таблица параметров, строка `page`, пример `page=2`; запрос `page=3` в примере пагинации
- **Покрытие:** Частично
- **Тесты и заметка:** **Пользовательские:** `tests/func/test_page.py::TestRegionsPage::test_page_valid_positive`
  проверяет только успешные непустые ответы для 2/3. **Агентские:**
  `agents-test/func/test_pagination_contract.py::TestRegionsPaginationContract::test_page_number_changes_selected_result`
  сравнивает `total` и проверяет `ids_page2 != ids_page3`. Не требует непересечения и не задаёт эталонные ID.

### API-013 — `GET /1.0/regions`, `page_size`
- **Требование и сценарий:** Проверить число элементов страницы для единственного читаемого значения из примера
  `page_size=5`; остальные значения/default неизвестны.
- **Ожидаемый результат:** Полная страница с достаточным числом записей содержит ровно 5 элементов.
- **Источник:** Стр. 2, описание `page_size` и пример `page=3&page_size=5`
- **Покрытие:** Частично
- **Тесты и заметка:** **Пользовательские:**
  `tests/func/test_page_size.py::TestRegionsPageSize::test_page_size_valid_values` проверяет ровно 5/10/15; 10/15 не
  подтверждены читаемым текстом. **Агентские:**
  `agents-test/func/test_pagination_contract.py::`
  `TestRegionsPaginationContract::test_documented_page_size_controls_full_page`
  проверяет ровно 5 для `page=3&page_size=5`. Допустимый список и default остаются неизвестными.

### API-014 — Задание 2, учебный пример проверки `total`
- **Требование и сценарий:** Отдельно от нормативной семантики API проверить кодовый пример задания `assert body['total']
  == 22`.
- **Ожидаемый результат:** В учебном примере ожидается именно 22; это тестовый пример/значение стенда, не самостоятельная
  спецификация семантики общего `total`.
- **Источник:** Стр. 3, строки 4–7, пример `test_total_count()`
- **Покрытие:** Покрыто (учебный пример)
- **Тесты и заметка:** **Пользовательские:** явного assert `total == 22` в `tests/func/` нет; там проверяется
  стабильность. **Агентские:**
  `agents-test/func/test_response_contract.py::TestRegionsResponseContract::test_total_matches_assignment_example`
  сравнивает `total == 22`. Нормативная семантика отдельно остаётся API-002 и частично покрыта.


## Непокрытые требования и пробелы

- **API-002:** проверки смены страницы есть и относятся к контрактному покрытию.
  Сравнения `page_size=5/10/15` и `country_code=ru` добавлены в агентскую suite
  (`test_total_stays_stable_across_page_sizes`,
  `test_total_with_country_filter_characterization`), но явно классифицированы
  как characterization. Пример `22` отдельно относится к API-014.
- **API-003:** агентская suite проверяет ID внутри страницы и consistency map
  `id -> tuple` между страницами (`test_ids_keep_the_same_entity_across_pages`).
  Второй assertion не доказывает глобальную уникальность: один и тот же видимый
  tuple может относиться к разным сущностям. API-003 остаётся частичным без
  независимого entity oracle.
- **API-011:** агентский тест проверяет inclusion четырёх упомянутых кодов, но не
  исключает неожиданные. Контракт не говорит, что допустимые значения фильтра —
  исчерпывающий список стран базы, поэтому equality без полного справочника
  недопустимо и coverage остаётся partial.
- **API-012:** проверяется изменение множества для page 2/3; точные результаты,
  сортировка и непересечение страниц не определены.
- **API-013:** проверяется только пример `page_size=5`; неизвестные разрешённые
  значения и default остаются непроверяемыми по извлечённому тексту.

## Вопросы и неопределённости

- В `tz-extracted.txt` NUL-символами заменены минимум `q`, минимум и default
  `page`, три значения и default `page_size`. Значения `q >= 3`, `page=1`,
  `page_size={5,10,15}` и default `15` из старых тестов не являются подтверждёнными
  требованиями без читаемого первоисточника.
- Контракт не задаёт HTTP-коды, формат/поля ошибок и ожидаемую реакцию на пустые,
  недопустимые или некорректные query-параметры. Негативные assertions в старых
  тестах не относятся к подтверждённому контрактному покрытию.
- Перечень `ru/kg/kz/cz` задан как допустимые значения фильтра; он не объявлен
  исчерпывающим перечнем стран в базе. Поэтому полноту «все страны» нельзя
  доказать equality с этими четырьмя кодами; нужен полный справочник или точное
  уточнение контракта.
- Контракт не определяет сортировку, точный состав страниц, непересечение ID между
  страницами или содержимое последней страницы. Такие ожидания нельзя добавлять
  как обязательные без уточнения.
- `total == 22` дано в учебном примере теста задания (стр. 3); отдельно подтвердить,
  что это постоянная нормативная величина API, по доступному тексту нельзя.
- Пример `GET /1.0/region?page=3&page_size=5` использует singular `/region`, тогда
  как endpoint выше указан `/regions`; точное поведение этого опечаточного пути не
  добавляется в требования.
- Проверки в этом чек-листе отражают наличие assertions в коде, а не результат
  последнего запуска. Фактические результаты прогонов и дефекты фиксируются
  отдельно в dated reports под `agents-test/bug/`.

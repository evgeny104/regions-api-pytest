# Regions API tests

Automated tests for the public 2GIS Regions API (`https://host/1.0/regions`). Cover the `q`, `country_code`, `page`, `page_size` parameters, their combinations, and pagination behavior.

## Stack

- Python 3.10+
- pytest — test runner
- requests — HTTP client
- pydantic — response schema validation
- allure-pytest — reporting

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
# source .venv/bin/activate      # Linux/macOS
pip install -r requirements.txt
```

## Configuration

`src/config/url.py` is not stored in the repository (see `.gitignore`). Create it manually:

```python
# src/config/url.py
BASE_URL = 'https://host/1.0/regions'
```

## Running tests

```bash

pytest -v                                 # default run
pytest --alluredir=allure-results         # produce Allure results
pytest tests/test_main.py::TestRegionsQ   # single class
pytest -k "page_size"                     # filter by test id substring
```

## Viewing the Allure report

Requires the [Allure CLI](https://allurereport.org/docs/install/).

```bash
allure serve allure-results                          # temporary local server
allure generate allure-results -o allure-report --clean
allure open allure-report
```

### Windows PowerShell example

```powershell
Remove-Item allure-results\* -Recurse -Force                                # Let's clear the reports
pytest tests/test_main.py::TestRegionsPage -v --alluredir=allure-results    # We are launching only TestRegionsPage
pytest -v --alluredir=allure-results                                        # Run all tests + report allure
allure serve allure-results                                                 # Open the report in the browser
```

## Docker

`BASE_URL` is passed at build time via `--build-arg` (request the actual value from the project owner).

```bash
docker build --build-arg BASE_URL=<BASE_URL> -t regions-tests .
docker run --rm -v "${PWD}/allure-results:/app/allure-results" regions-tests
```

## Project layout

```
.
├── main.py                       # Region wrapper over requests + network error classification
├── conftest.py                   # region_response / region_response_pair fixtures, Allure grouping
├── src/
│   ├── config/url.py             # BASE_URL (create locally)
│   └── models/Pydantic/region.py # Pydantic response models (RegionResponse, RegionErrorResponse)
└── tests/
    └── test_main.py              # tests grouped by parameter under test
```
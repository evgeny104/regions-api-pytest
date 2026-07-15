FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py conftest.py ./
COPY src ./src
COPY tests ./tests

ARG BASE_URL
RUN test -n "$BASE_URL" || (echo "ERROR: --build-arg BASE_URL is required" && exit 1) \
    && mkdir -p src/config \
    && printf "BASE_URL = '%s'\n" "$BASE_URL" > src/config/url.py \
    && touch src/config/__init__.py src/__init__.py

RUN groupadd --gid 1000 tester \
    && useradd  --uid 1000 --gid tester --create-home tester \
    && mkdir -p /app/allure-results \
    && chown -R tester:tester /app
USER tester

VOLUME ["/app/allure-results"]

ENTRYPOINT ["pytest"]
CMD ["-v", "--alluredir=allure-results"]
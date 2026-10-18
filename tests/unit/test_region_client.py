import pytest
import requests
from requests.exceptions import Timeout, SSLError, ConnectionError, RequestException

from src.api.region_client import Region


class TestGetParams:
    """Region.get_params — отбрасывает None, остальное сохраняет."""

    def test_all_params_preserved(self):
        """Все четыре параметра сохраняются, когда заданы."""
        region = Region(url="http://x", q="нов", country_code="ru", page=1, page_size=5)
        assert region.get_params() == {
            "q": "нов", "country_code": "ru", "page": 1, "page_size": 5,
        }

    def test_only_none_dropped(self):
        """Отбрасываются только None; falsy не-None (например 0) сохраняются."""
        region = Region(url="http://x", q="нов", page=0)
        assert region.get_params() == {"q": "нов", "page": 0}

    def test_empty_when_nothing_set(self):
        """Ни одного параметра → пустой dict."""
        region = Region(url="http://x")
        assert region.get_params() == {}


class TestGetDataNetworkErrors:
    """Region.get_data — классифицирует подклассы RequestException по id."""

    @pytest.mark.parametrize(
        "exc_cls, expected_id",
        [
            pytest.param(Timeout,          "network_timeout",          id="timeout"),
            pytest.param(SSLError,         "network_ssl_error",        id="ssl"),
            pytest.param(ConnectionError,  "network_connection_error", id="connection"),
            pytest.param(RequestException, "network_error",            id="generic"),
        ],
    )
    def test_network_errors_classified(self, monkeypatch, exc_cls, expected_id):
        """Каждый известный подкласс RequestException маппится в конкретный error id."""
        def _fail(*args, **kwargs):
            raise exc_cls("boom")

        monkeypatch.setattr(requests, "get", _fail)
        region = Region(url="http://x")
        status, data = region.get_data()

        assert status is None
        assert data["error"]["id"] == expected_id
        assert "boom" in data["error"]["message"]


class TestGetDataInvalidJson:
    """Region.get_data — маппит не-JSON тело в error id = server_invalid_json."""

    def test_non_json_response(self, monkeypatch):
        """Когда response.json() бросает — возвращаем server_invalid_json с исходным текстом."""

        class _Resp:
            status_code = 200
            text = "not a json body"

            def json(self):
                raise ValueError("no json")

        monkeypatch.setattr(requests, "get", lambda *a, **kw: _Resp())
        region = Region(url="http://x")
        status, data = region.get_data()

        assert status == 200
        assert data["error"]["id"] == "server_invalid_json"
        assert data["error"]["message"] == "not a json body"

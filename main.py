import requests
from requests.exceptions import Timeout, ConnectionError, SSLError, RequestException

DEFAULT_TIMEOUT = 15

NETWORK_ERROR_IDS = {
    Timeout: "network_timeout",
    SSLError: "network_ssl_error",
    ConnectionError: "network_connection_error",
}


class Region:
    def __init__(self, url=None, q=None, country_code=None, page=None, page_size=None):
        self.url = url
        self.q = q
        self.country_code = country_code
        self.page = page
        self.page_size = page_size

    def get_params(self):
        return {
            k: v for k, v in (
                ("q", self.q),
                ("country_code", self.country_code),
                ("page", self.page),
                ("page_size", self.page_size),
            ) if v is not None
        }

    def get_data(self, timeout=DEFAULT_TIMEOUT):
        try:
            response = requests.get(self.url, params=self.get_params(), timeout=timeout)
        except RequestException as exc:
            error_id = next(
                (eid for exc_type, eid in NETWORK_ERROR_IDS.items() if isinstance(exc, exc_type)),
                "network_error",
            )
            return None, {"error": {"id": error_id, "message": str(exc)[:500]}}

        try:
            data = response.json()
        except ValueError:
            data = {"error": {"id": "server_invalid_json",
                              "message": response.text[:500]}}
        return response.status_code, data

    def __repr__(self):
        return (f"Region(url={self.url!r}, q={self.q!r}, "
                f"country_code={self.country_code!r}, "
                f"page={self.page!r}, page_size={self.page_size!r})")

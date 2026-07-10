import requests

DEFAULT_TIMEOUT = 15


class Region:
    def __init__(self, url=None, q=None, country_code=None, page_size=None, page=None):
        self.url = url
        self.q = q
        self.country_code = country_code
        self.page_size = page_size
        self.page = page
        self.data = None
        self.status_code = None

    def get_params(self):
        params = {}
        if self.q is not None:
            params['q'] = self.q
        if self.country_code is not None:
            params['country_code'] = self.country_code
        if self.page_size is not None:
            params['page_size'] = self.page_size
        if self.page is not None:
            params['page'] = self.page
        return params

    def get_data(self, timeout=DEFAULT_TIMEOUT):
        response = requests.get(self.url, params=self.get_params(), timeout=timeout)
        self.status_code = response.status_code
        self.data = response.json()
        return self.status_code, self.data

    def __repr__(self):
        return f"Region(status_code={self.status_code}, data={self.data})"

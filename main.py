import requests

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
        if self.q:
            params['q'] = self.q
        if self.country_code:
            params['country_code'] = self.country_code
        if self.page_size:
            params['page_size'] = self.page_size
        if self.page:
            params['page'] = self.page
        return params

    def get_data(self):
        response = requests.get(self.url, params=self.get_params())
        self.status_code = response.status_code
        self.data = response.json()
        return self.status_code, self.data

    def __repr__(self):
        return self.status_code, self.data

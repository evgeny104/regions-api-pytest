import pytest
from main import Region
from src.config.url import BASE_URL

@pytest.fixture
def region_response(request):
    """Creates a Region object and returns status_code and data."""
    q, country_code, page_size, page = request.param

    region = Region(
        url=BASE_URL,
        q=q,
        country_code=country_code,
        page_size=page_size,
        page=page
    )
    # Unpacking the (status_code, data) tuple.
    data, status_code = region.get_data()
    return data, status_code
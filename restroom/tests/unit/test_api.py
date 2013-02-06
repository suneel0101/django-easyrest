from restroom import API
from sure import expect


def test_get_url_data():
    api = API()
    url_data = api.get_url_data('table_model', {})
    expected_data = {
        'regex': r'^table_model/$',
        'view': 'restroom.views.base',
        'name': 'table_model_api',
    }
    expect(url_data).to.equal(expected_data)

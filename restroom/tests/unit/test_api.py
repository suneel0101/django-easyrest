from restroom import API
from sure import expect


def test_get_url_data():
    # Given a restroom API instance
    api = API()
    # When I get the url_data for the table `table_model`
    # with data {}
    url_data = api.get_url_data('table_model', {})

    # I should get back a dictionary containing
    # the URL Regex, the View string and the URL name
    expected_data = {
        'regex': r'^table_model/$',
        'view': 'restroom.views.base',
        'name': 'table_model_api',
    }
    expect(url_data).to.equal(expected_data)

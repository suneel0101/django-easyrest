from restroom import API
from mock import Mock
from sure import expect
from django.conf.urls import url, patterns


def transform_to_attrs_dict(url_patterns):
    """
    Transforms url patterns to dictionaries of
    their attributes (regex, view and name)
    """
    return [{'regex': pattern._regex,
             'view': pattern._callback_str,
             'name': pattern.name}
            for pattern in url_patterns]


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


def test_api_url_data_property():
    # Given a restroom API instance
    api = API()

    # And we have two models, MyModel and YourModel
    MyModel = Mock()
    MyModel._meta.fields = [Mock(attname='id'), Mock(attname='text')]
    MyModel._meta.db_table = "table_mymodel"

    YourModel = Mock()
    YourModel._meta.fields = [Mock(attname='id'), Mock(attname='name')]
    YourModel._meta.db_table = "table_yourmodel"

    # And we register these models to the api
    api.register(MyModel)
    api.register(YourModel)

    # We should get back a list of dictionaries containing
    # the url data for each of these models
    # when we call url_data
    expected_data = [
        {
            'regex': r'^table_mymodel/$',
            'view': 'restroom.views.base',
            'name': 'table_mymodel_api',
        },
        {
            'regex': r'^table_yourmodel/$',
            'view': 'restroom.views.base',
            'name': 'table_yourmodel_api',
        },
    ]
    expect(api.url_data).to.equal(expected_data)


def test_api_construct_url_pattern():
    # Given a restroom API instance
    api = API()

    url_data = [{
        'regex': r'^table_mymodel/$',
        'view': 'restroom.views.base',
        'name': 'table_mymodel_api',
    }]

    url_patterns = api.construct_url_patterns(url_data)
    expected_patterns = patterns('',
        url(r'^table_mymodel/$',
            'restroom.views.base',
            name='table_mymodel_api'),
    )

    (expect(transform_to_attrs_dict(url_patterns))
     .to.equal(transform_to_attrs_dict(expected_patterns)))


def test_api_url_patterns():
    # Given a restroom API instance
    api = API()

    # And we have two models, MyModel and YourModel
    MyModel = Mock()
    MyModel._meta.fields = [Mock(attname='id'), Mock(attname='text')]
    MyModel._meta.db_table = "table_mymodel"

    YourModel = Mock()
    YourModel._meta.fields = [Mock(attname='id'), Mock(attname='name')]
    YourModel._meta.db_table = "table_yourmodel"

    # And we register these models to the api
    api.register(MyModel)
    api.register(YourModel)

    expected_patterns = patterns('',
        url(r'^table_mymodel/$',
            'restroom.views.base',
            name='table_mymodel_api'),
        url(r'^table_yourmodel/$',
            'restroom.views.base',
            name='table_yourmodel_api'),

    )
    url_patterns = api.url_patterns

    (expect(transform_to_attrs_dict(url_patterns))
     .to.equal(transform_to_attrs_dict(expected_patterns)))

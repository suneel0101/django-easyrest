import ast

from restroom import API, RestroomError
from mock import Mock
from sure import expect
from django.conf.urls import url, patterns
from django.http import QueryDict

def transform_to_attrs_dict(url_patterns):
    """
    Transforms url patterns to dictionaries of
    their attributes (regex, view and name)
    """
    return [{'regex': pattern._regex,
             'view': pattern._callback_str,
             'name': pattern.name}
            for pattern in url_patterns]


def test_validate_registration_invalid_fields_raises_error():
    api = API()

    model_class = Mock()
    fields = [
        Mock(attname='id'),
        Mock(attname='text'),
        Mock(attname='status'),
    ]
    model_class._meta = Mock(fields=fields, object_name='MyModel')
    options = {
        'fields': ['id', 'timestamp']
    }
    (api.register
     .when.called_with(model_class, options)
     .should
     .throw(RestroomError, "timestamp is not a valid field of MyModel"))


def test_validate_fields_with_valid_fields():
    api = API()

    (expect(api.validate_fields(
                ['id', 'address'],
                ['id', 'address', 'city', 'ZIP']))
     .to.equal((True, None)))


def test_validate_fields_with_invalid_fields():
    api = API()

    (expect(api.validate_fields(
                ['id', 'name'],
                ['id', 'address', 'city', 'ZIP']))
     .to.equal((False, 'name')))


def test_validate_allowed_methods_with_valid_methods():
    api = API()

    (expect(api.validate_allowed_methods(
                ['GET', 'POST']))
     .to.equal((True, None)))


def test_validate_allowed_methods_with_invalid_methods():
    api = API()

    (expect(api.validate_allowed_methods(
                ['GET', 'RANDOMMETHOD']))
     .to.equal((False, 'RANDOMMETHOD')))


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


def test_url_patterns():
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


def test_generate_list_view_for_get():
    # Given a restroom API instance
    api = API()

    # And we have a model
    MyModel = Mock()
    MyModel._meta.fields = [Mock(attname='id'), Mock(attname='text')]
    MyModel._meta.db_table = "table_mymodel"

    MyModel.objects.values.return_value = [{'id': 1, 'text': 'Shalom'}]
    # And we register this model to the api
    api.register(MyModel)

    # The api view that is generated by api.generate_view
    # should return the expected json data when requested
    # via GET
    request = Mock(method='GET')
    response_from_GET = (api.generate_list_view("table_mymodel")
                         .as_view()(request))
    expected_response_json = [{'id': 1, 'text': 'Shalom'}]
    response_json = ast.literal_eval(response_from_GET.content)
    expect(response_json).to.equal(expected_response_json)


def test_generate_list_view_for_post():
    # Given a restroom API instance
    api = API()

    # And we have a model
    MyModel = Mock()
    MyModel._meta.fields = [Mock(attname='id'), Mock(attname='text')]
    MyModel._meta.db_table = "table_mymodel"

    # We mock the return of Django .create
    # to be an object with id 1 and text=Shalom
    # whose __class__._meta.db_table is `table_mymodel`
    returned_obj = Mock()
    returned_obj.id = 1
    returned_obj.text = 'Shalom'
    _meta = Mock(db_table='table_mymodel')
    returned_obj.__class__ = Mock(_meta=_meta)
    MyModel.objects.create.return_value = returned_obj

    # And we register this model to the api
    api.register(MyModel, {'allowed_methods': ['GET', 'POST']})

    # The api view that is generated by api.generate_view
    # should return the expected json data when requested
    # via POST
    request = Mock(method='POST')
    request.POST = QueryDict('text=Shalom')
    response_from_POST = (api.generate_list_view("table_mymodel")
                          .as_view()(request))
    expected_response_json = {'id': 1, 'text': 'Shalom'}
    response_json = ast.literal_eval(response_from_POST.content)
    expect(response_json).to.equal(expected_response_json)
    MyModel.objects.create.assert_called_once_with(text='Shalom')


def test_generate_single_item_view_for_get():
    # Given a restroom API instance
    api = API()

    # And we have a model
    MyModel = Mock()
    fields = [Mock(attname='id'), Mock(attname='text')]
    db_table = "table_mymodel"
    _meta = Mock(fields=fields, db_table=db_table)
    MyModel._meta = _meta

    _id = 1

    returned_object = Mock()
    returned_object.id = _id
    returned_object.text = 'Shalom'
    returned_object.__class__ = MyModel
    MyModel.objects.get.return_value = returned_object

    MyModel.objects.values.return_value = [{'id': _id, 'text': 'Shalom'}]
    # And we register this model to the api
    api.register(MyModel)

    # The api view that is generated by api.generate_view
    # should return the expected json data when requested
    # via GET
    request = Mock(method='GET')
    response_from_GET = (api.generate_single_item_view("table_mymodel")
                         .as_view()(request, _id))
    expected_response_json = {'id': _id, 'text': 'Shalom'}
    response_json = ast.literal_eval(response_from_GET.content)
    expect(response_json).to.equal(expected_response_json)

from restroom import API, RestroomError
from mock import Mock
from sure import expect
from django.conf.urls import url, patterns

from restroom.views import (RestroomListView,
                            RestroomSingleItemView)


def transform_to_attrs_dict(url_patterns):
    """
    Transforms url patterns to dictionaries of
    their attributes (regex, view and name)
    """
    # TODO:
    # This is a bit of a black box, please explain what is happening
    # with func_closure
    return [{'regex': pattern._regex,
             'view_func_name': pattern.callback.func_name,
             'allowed_methods': pattern.callback.func_closure[0].cell_contents['allowed_methods'],
             'table_name': pattern.callback.func_closure[0].cell_contents['table_name'],
             'api_class_name': pattern.callback.func_closure[0].cell_contents['api'].__class__.__name__,
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

    (expect(api.validate_fields(['id', 'address'],
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


def test_validate_registration_invalid_http_methods_raises_error():
    api = API()

    model_class = Mock()
    fields = [
        Mock(attname='id'),
        Mock(attname='text'),
        Mock(attname='status'),
    ]
    model_class._meta = Mock(fields=fields, object_name='MyModel')
    options = {
        'fields': ['id', 'text'],
        'allowed_methods': ['GET', 'HELLO']
    }
    (api.register
     .when.called_with(model_class, options)
     .should
     .throw(RestroomError, "HELLO is not a valid allowable HTTP method"))


def test_get_urls():
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
    my_list_view = RestroomListView.as_view(api=api,
                                         allowed_methods=['GET'],
                                         table_name='table_mymodel')
    your_list_view = RestroomListView.as_view(api=api,
                                         allowed_methods=['GET'],
                                         table_name='table_yourmodel')

    my_single_item_view = RestroomSingleItemView.as_view(api=api,
                                         allowed_methods=['GET'],
                                         table_name='table_mymodel')

    your_single_item_view = RestroomSingleItemView.as_view(api=api,
                                         allowed_methods=['GET'],
                                         table_name='table_yourmodel')

    expected_patterns = patterns('',
                                 url(r'^table_mymodel/$',
                                     my_list_view,
                                     name='table_mymodel_list_api'),
                                 url(r'^table_mymodel/(?P<_id>[\d]+)/$',
                                     my_single_item_view,
                                     name='table_mymodel_single_item_api'),
                                 url(r'^table_yourmodel/$',
                                     your_list_view,
                                     name='table_yourmodel_list_api'),
                                 url(r'^table_yourmodel/(?P<_id>[\d]+)/$',
                                     your_single_item_view,
                                     name='table_yourmodel_single_item_api'),
                                 )
    url_patterns = api.get_urls()

    (expect(transform_to_attrs_dict(url_patterns))
     .to.equal(transform_to_attrs_dict(expected_patterns)))

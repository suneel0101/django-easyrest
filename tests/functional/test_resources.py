from restroom.resources import RestroomResource
from mock import Mock
from sure import expect, scenario
from restroom.errors import (
    RestroomInvalidFieldError,
    RestroomInvalidHTTPMethodError)


def prepare_model(context):
    model = Mock()
    model._meta.db_table = 'table_model'
    id_field = Mock(attname='id')
    text_field = Mock(attname='text')
    slug_field = Mock(attname='slug')
    model._meta.fields = [id_field, text_field, slug_field]
    context.field_map = {
        'id': id_field,
        'text': text_field,
        'slug': slug_field,
    }
    context.model = model


@scenario(prepare_model)
def test_default_initialization(context):
    "Initialization without any options"
    resource = RestroomResource(context.model)
    expect(resource.http_methods).to.equal(['GET'])
    expect(resource.field_map).to.equal(context.field_map)
    expect(resource.model).to.equal(context.model)


@scenario(prepare_model)
def test_initialization_with_nondefault_http_methods(context):
    "Initialization with specified http_methods"
    resource = RestroomResource(context.model,
                                {'http_methods': ['POST', 'PUT']})
    expect(resource.http_methods).to.equal(['POST', 'PUT'])
    expect(resource.field_map).to.equal(context.field_map)
    expect(resource.model).to.equal(context.model)


@scenario(prepare_model)
def test_initialization_with_nondefault_fields(context):
    "Initialization with specified fields"
    resource = RestroomResource(context.model,
                                {'http_methods': ['POST', 'PUT'],
                                'fields': ['id', 'text']})
    expect(resource.http_methods).to.equal(['POST', 'PUT'])
    expect(resource.field_map).to.equal({'id': context.field_map['id'],
                                         'text': context.field_map['text']})
    expect(resource.model).to.equal(context.model)


@scenario(prepare_model)
def test_initialization_with_nondefault_fields_without_id(context):
    "Initialization with specified fields should have id even if unspecified"
    resource = RestroomResource(context.model,
                                {'http_methods': ['POST', 'PUT'],
                                'fields': ['text']})
    expect(resource.http_methods).to.equal(['POST', 'PUT'])
    expect(resource.field_map).to.equal({'id': context.field_map['id'],
                                         'text': context.field_map['text']})
    expect(resource.model).to.equal(context.model)


@scenario(prepare_model)
def test_initialization_with_invalid_field_name(context):
    "Invalid field name raises RestroomInvalidFieldError"
    (RestroomResource.when.called_with(context.model,
                                {'http_methods': ['POST', 'PUT'],
                                'fields': ['id', 'name']})
     .should.throw(RestroomInvalidFieldError,
                   "Cannot resolve the following field names: name"))


@scenario(prepare_model)
def test_initialization_with_invalid_http_method(context):
    "Invalid http method raises RestroomInvalidHTTPMethodError"
    (RestroomResource.when.called_with(context.model,
                                {'http_methods': ['PRESS', 'PUT'],
                                'fields': ['id', 'text']})
     .should.throw(RestroomInvalidHTTPMethodError,
                   "The following are invalid HTTP methods: PRESS"))

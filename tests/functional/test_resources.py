from restroom.resources import RestroomResource
from mock import Mock
from sure import expect, scenario
from restroom.errors import (
    RestroomInvalidFieldError,
    RestroomInvalidHTTPMethodError,
    RestroomInvalidOperatorError,
    RestroomMalformedFilterError)

from tests.models import Modelo


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


def prepare_real_model(context):
    Modelo.objects.all().delete()

    Modelo.objects.create(
        text='Some text',
        slug='a-slug',
        awesome=True)

    Modelo.objects.create(
        text='Some more text',
        slug='b-slug',
        awesome=False)


def delete_modelo_objects(context):
    Modelo.objects.all().delete()


@scenario([prepare_real_model], [delete_modelo_objects])
def test_retrieve(context):
    "Default retrieve with no filters and no page passed in"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})

    expect(resource.retrieve()).to.equal({'items': [{'id': 1,
                                                     'text': 'Some text',
                                                     'slug': 'a-slug',
                                                     'awesome': True},
                                                    {'id': 2,
                                                     'text': 'Some more text',
                                                     'slug': 'b-slug',
                                                     'awesome': False}]})


@scenario([prepare_real_model], [delete_modelo_objects])
def test_retrieve_with_valid_filters(context):
    "Retrieving and filtering"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})
    filters = [
        {'field': 'id', 'operator': 'lt', 'value': 2},
        {'field': 'text', 'operator': 'icontains', 'value': 'text'},
    ]
    expect(resource.retrieve(filters=filters)).to.equal({'items': [{'id': 1,
                                                     'text': 'Some text',
                                                     'slug': 'a-slug',
                                                     'awesome': True}]})


@scenario([prepare_real_model], [delete_modelo_objects])
def test_retrieve_with_equals_filter(context):
    "Retrieving and filtering with exact"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})
    filters = [
        {'field': 'id', 'operator': 'exact', 'value': 1},
    ]
    expect(resource.retrieve(filters=filters)).to.equal({'items': [{'id': 1,
                                                     'text': 'Some text',
                                                     'slug': 'a-slug',
                                                     'awesome': True}]})


@scenario([prepare_real_model], [delete_modelo_objects])
def test_retrieve_with_invalid_filters(context):
    "Retrieval with invalid filters should raise RestroomInvalidFieldError"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})
    filters = [
        {'field': 'crazy', 'operator': 'lt', 'value': 2},
    ]
    (resource.retrieve.when.called_with(filters=filters)
     .should.throw(RestroomInvalidFieldError,
                "Cannot resolve the following field names: crazy"))


@scenario([prepare_real_model], [delete_modelo_objects])
def test_retrieve_with_invalid_operators(context):
    "Retrieval with invalid operators raises RestroomInvalidOperatorError"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})
    filters = [
        {'field': 'id', 'operator': 'blah', 'value': 2},
    ]
    (resource.retrieve.when.called_with(filters=filters)
     .should.throw(RestroomInvalidOperatorError,
                "The following are invalid filter operators: blah"))


@scenario([prepare_real_model], [delete_modelo_objects])
def test_retrieve_with_malformed_filters_list(context):
    "Retrieval with invalid operators raises RestroomInvalidOperatorError"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})
    filters = [
        {'field': 'id', 'operator': 'exact'},
    ]
    (resource.retrieve.when.called_with(filters=filters)
     .should.throw(RestroomMalformedFilterError,
                   "Received a malformed filter"))


@scenario([prepare_real_model], [delete_modelo_objects])
def test_retrieve_one(context):
    "Retrieve one"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})
    expect(resource.retrieve_one(1)).to.equal({'id': 1,
                                               'text': 'Some text',
                                               'slug': 'a-slug',
                                               'awesome': True})


@scenario([prepare_real_model], [delete_modelo_objects])
def test_retrieve_nonexistent_one(context):
    "Retrieve one for nonexistent id returns error JSON"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})
    expect(resource.retrieve_one(4)).to.equal(
        {'error': 'No result matches id: 4'})


@scenario([prepare_real_model], [delete_modelo_objects])
def test_delete(context):
    "Delete"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})
    expect(resource.delete(1)).to.equal({})


@scenario([prepare_real_model], [delete_modelo_objects])
def test_delete_nonexistent(context):
    "Delete nonexistent model returns error JSON"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})
    expect(resource.delete(5)).to.equal({'error': 'No result matches id: 5'})


@scenario([prepare_real_model], [delete_modelo_objects])
def test_create(context):
    "Create"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})

    (expect(resource.create(
            {'text': 'Awesome text', 'slug': 'awesome-slug', 'awesome': True}))
     .to.equal({'id': 3,
                'text': 'Awesome text',
                'slug': 'awesome-slug',
                'awesome': True})
     )


@scenario([prepare_real_model], [delete_modelo_objects])
def test_create_with_invalid_fields(context):
    "Create with invalid fields raises error"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})

    (resource.create.when.called_with(
            {'blah': 'Awesome text', 'slug': 'awesome-slug', 'awesome': True})
     .should.throw(RestroomInvalidFieldError,
                   "Cannot resolve the following field names: blah"))


@scenario([prepare_real_model], [delete_modelo_objects])
def test_create_with_failure_at_model_level(context):
    "Create that fails at the model level, e.g. nonunique slug"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})

    expect(resource.create(
            {'text': 'Awesome text',
             'slug': 'a-slug',
             'awesome': True})).to.equal(
        {'error': 'column slug is not unique'})


@scenario([prepare_real_model], [delete_modelo_objects])
def test_update_one(context):
    "Update_one"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})

    expect(resource.update_one(1,
            {'text': 'Amazing text'})).to.equal(
        {'id': 1,
         'text': 'Amazing text',
         'slug': 'a-slug',
         'awesome': True})


@scenario([prepare_real_model], [delete_modelo_objects])
def test_update_nonexistent_one(context):
    "Update nonexistent one"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})

    expect(resource.update_one(4,
            {'text': 'Amazing text'})).to.equal(
        {'error': 'No result matches id: 4'})


@scenario([prepare_real_model], [delete_modelo_objects])
def test_update_one_with_changed_id(context):
    "Update_one with changed id does not change the id"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})

    expect(resource.update_one(1,
            {'id': 5,
             'text': 'Baller text',
             'slug': 'awesome-slug',
             'awesome': True})).to.equal({
                'id': 1,
                'text': 'Baller text',
                'slug': 'awesome-slug',
                'awesome': True})


@scenario([prepare_real_model], [delete_modelo_objects])
def test_update_one_when_failure_at_model_level(context):
    "Update_one fails at the model level"
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})

    expect(resource.update_one(1,
            {'text': 'Baller text',
             'slug': 'b-slug',
             'awesome': True})).to.equal(
        {'error': 'column slug is not unique'})

from tests.models import MyModel
from restroom import API, expose
from sure import expect

from django.db import models


def test_registering_a_model_adds_it_to_the_table_model_map():
    # Given a restroom api and a model
    restroom_api = API()
    restroom_api.register(MyModel)

    expected_dict = {
        'model': MyModel,
        'fields': ['id', 'name'],
        'allowed_methods': ['GET'],
    }

    # fields in model_data should match all of MyModel's fields
    # as no `fields` option was passed into register
    (expect([field.attname for field in MyModel._meta.fields])
     .to.equal(expected_dict['fields']))

    # and the model_data should be the default
    (expect(restroom_api.table_model_map['tests_mymodel'])
    .to.equal(expected_dict))


def test_registering_with_non_default_options():
    restroom_api = API()
    restroom_api.register(MyModel,
                 {'allowed_methods': ['POST'],
                  'fields': ['name']})
    expected_dict = {
        'model': MyModel,
        'fields': ['name'],
        'allowed_methods': ['POST'],
    }

    # Since we specified 'POST' and only want to expose the `name` field
    # The model_data `fields` should be just ['name'] and the only allowable
    # method of calling this resource should be POST
    (expect(restroom_api.table_model_map['tests_mymodel'])
     .to.equal(expected_dict))


def test_expose_with_no_arguments():

    restroom_api = API()

    # When we decorate a Django Model with expose
    @expose(api=restroom_api)
    class ExposedModel(models.Model):
        title = models.CharField(max_length=150)
        active = models.BooleanField(default=False)

    table_name = ExposedModel._meta.db_table
    registered_value = restroom_api.table_model_map[table_name]

    expected_value = {
        'model': ExposedModel,
        'fields': ['id', 'title', 'active'],
        'allowed_methods': ['GET'],
    }
    # It registers it correctly with the Restroom API
    expect(registered_value).to.equal(expected_value)


def test_expose_with_options():

    # When we decorate a Django Model with expose and
    # non-default options of allowable methods
    # and exposed fields
    restroom_api = API()

    @expose(api=restroom_api,
            allowed_methods=['GET', 'POST'],
            fields=['short_title', 'author'])

    class ExposedModelWithOptions(models.Model):
        short_title = models.CharField(max_length=150)
        expired = models.BooleanField(default=False)
        author = models.CharField(max_length=120)
        status = models.IntegerField(default=1)

    table_name = ExposedModelWithOptions._meta.db_table
    registered_value = restroom_api.table_model_map[table_name]

    expected_value = {
        'model': ExposedModelWithOptions,
        'fields': ['short_title', 'author'],
        'allowed_methods': ['GET', 'POST'],
    }

    # It should register it correctly with the Restroom API
    expect(registered_value).to.equal(expected_value)


def test_retrieval():
    from tests.models import (
        ExposedModelToSerialize,
        exposed_model_to_serialize_api)

    table_name = ExposedModelToSerialize._meta.db_table

    # When we delete all existing ExposedModelToSerialize objects
    ExposedModelToSerialize.objects.all().delete()

    # And we create an ExposedModelToSerialize object
    exposed_model_obj = ExposedModelToSerialize.objects.create(
        short_title="This is a short title",
        author="Edgar Allen Poe",
    )
    _id = exposed_model_obj.id

    # and retrieve this data from the database using the retrieve
    # method of the Restroom API
    serialized_data = exposed_model_to_serialize_api.retrieve(table_name)

    expected_data = [
        {
            'id': _id,
            'short_title': 'This is a short title',
            'author': "Edgar Allen Poe",
        },
    ]
    # We should get back the expected serialized data
    expect(serialized_data).to.equal(expected_data)
    exposed_model_obj.delete()


def test_retrieve_one_with_existent_record():
    from tests.models import (
        ExposedModelToSerialize,
        exposed_model_to_serialize_api)

    table_name = ExposedModelToSerialize._meta.db_table

    # When we delete all existing ExposedModelToSerialize objects
    ExposedModelToSerialize.objects.all().delete()

    # And we create an ExposedModelToSerialize object
    exposed_model_obj = ExposedModelToSerialize.objects.create(
        short_title="This is a short title",
        author="Edgar Allen Poe",
    )
    _id = exposed_model_obj.id

    # and retrieve this data from the database using the retrieve_one
    # method of the Restroom API
    serialized_data = exposed_model_to_serialize_api.retrieve_one(table_name, _id)

    expected_data = {
        'id': _id,
        'short_title': 'This is a short title',
        'author': "Edgar Allen Poe",
    }

    # We should get back the expected serialized data
    expect(serialized_data).to.equal(expected_data)
    exposed_model_obj.delete()


def test_retrieve_one_for_nonexistent_record():
    from tests.models import (
        ExposedModelToSerialize,
        exposed_model_to_serialize_api)

    table_name = ExposedModelToSerialize._meta.db_table

    # When we delete all existing ExposedModelToSerialize objects
    ExposedModelToSerialize.objects.all().delete()

    # and we try to retrieve_one record of id = 1
    serialized_data = exposed_model_to_serialize_api.retrieve_one(table_name, 1)

    expected_data = {
        'error': 'no matching object found for id: 1'
    }

    # We should get back the expected serialized data
    expect(serialized_data).to.equal(expected_data)


def test_serialize_one():
    from tests.models import (
        ExposedModelToSerialize,
        exposed_model_to_serialize_api)

    # When we delete all existing ExposedModelToSerialize objects
    ExposedModelToSerialize.objects.all().delete()

    # Create an ExposedModelToSerialize object
    obj = ExposedModelToSerialize.objects.create(
        author='John Steinbeck',
        short_title='Grapes of Wrath')

    serialized_obj = exposed_model_to_serialize_api.serialize_one(obj)
    expected_serialized_obj = {
        'id': obj.id,
        'author': 'John Steinbeck',
        'short_title': 'Grapes of Wrath',
    }


def test_create_record():
    from tests.models import (
        ExposedModelToSerialize,
        exposed_model_to_serialize_api)

    table_name = ExposedModelToSerialize._meta.db_table

    # When we delete all existing ExposedModelToSerialize objects
    ExposedModelToSerialize.objects.all().delete()

    _api = exposed_model_to_serialize_api
    record = _api.create_record(
        'tests_exposedmodeltoserialize',
        {
            'author': 'James Joyce',
            'expired': True,
            'short_title': 'The Dubliners'
        })

    _id = record['id']

    # and we try to get record where id = _id through
    # the Django ORM
    _object = ExposedModelToSerialize.objects.get(id=_id)

    # We expect that the object should be the one we created
    expect(_object.author).to.equal('James Joyce')
    expect(_object.expired).to.equal(True)
    expect(_object.short_title).to.equal('The Dubliners')
    expect(_object.status).to.equal(1)
    expect(_object.id).to.equal(_id)

    _object.delete()


def test_create_record_where_model_validation_fails():
    from tests.models import (
        another_test_api,
        AnotherModel,
    )

    # When we delete all existing AnotherModel objects
    AnotherModel.objects.all().delete()

    _api = another_test_api

    record_1 = _api.create_record(
        'tests_anothermodel',
        {
            'text': 'Some text',
            'slug': 'coolest-ever'
        })

    # since we are creating a record with the same slug
    # and the slug is unique=True in the model declaration
    record_2 = _api.create_record(
        'tests_anothermodel',
        {
            'text': 'Some more text',
            'slug': 'coolest-ever'
        })

    # We expect to receive an error message about this
    expect(record_2).to.equal({'error': 'column slug is not unique'})

    # Delete all existing AnotherModel objects
    AnotherModel.objects.all().delete()

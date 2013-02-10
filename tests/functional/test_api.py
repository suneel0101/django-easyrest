import ast
import datetime
from mock import Mock
from tests.models import MyModel
from restroom import API, expose
from sure import expect

from django.db import models
from django.http import HttpResponseBadRequest


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


def test_retrieval_with_filter_params():
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

    another_obj = ExposedModelToSerialize.objects.create(
        short_title="This is another short title",
        author="Robert Frost",
    )

    another_id = another_obj.id

    # and retrieve this data from the database using the retrieve
    # method of the Restroom API
    serialized_data = exposed_model_to_serialize_api.retrieve(
        table_name,
        [{'field': 'short_title',
         'operator': '=',
         'value': 'This is a short title'}])

    expected_data = [
        {
            'id': _id,
            'short_title': 'This is a short title',
            'author': "Edgar Allen Poe",
        },
    ]
    # We should get back the expected serialized data
    expect(serialized_data).to.equal(expected_data)

    multiple_results = exposed_model_to_serialize_api.retrieve(
        table_name,
        [{'field': 'id',
         'operator': 'in',
         'value': [_id, another_id]
          }])

    expected_multiple_data = [
        {
            'id': _id,
            'short_title': 'This is a short title',
            'author': "Edgar Allen Poe",
        },
        {
            'id': another_id,
            'short_title': 'This is another short title',
            'author': "Robert Frost",
        },

    ]

    (expect(multiple_results)
     .to.equal(expected_multiple_data))

    exposed_model_obj.delete()
    another_obj.delete()


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
    serialized_data = (exposed_model_to_serialize_api
                       .retrieve_one(table_name, _id))

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
    serialized_data = (exposed_model_to_serialize_api
                       .retrieve_one(table_name, 1))

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
    expect(serialized_obj).to.equal(expected_serialized_obj)


def test_serialize_one_with_foreign_key():
    from tests.models import (
        test_api,
        ModelWithFK,
        ExposedFK,
        MyFK,
    )

    # When we delete all existing
    # MyFK, ExposedFK and ModelWithFK objects
    ModelWithFK.objects.all().delete()
    MyFK.objects.all().delete()
    ExposedFK.objects.all().delete()

    # Create an ExposedFK object
    exposed_fk = ExposedFK.objects.create(
        slug='awesome-slug',
        awesome=False,
        slogan='I am the best model ever!',
    )

    # Create a MyFK object
    my_fk = MyFK.objects.create(
        active=True,
        name='Foreign Keyson',
        exposed_fk=exposed_fk,
    )

    # Create an ModelWithFK object
    model_with_fk = ModelWithFK.objects.create(
        text='It was the best of times',
        my_fk=my_fk)

    serialized_obj = test_api.serialize_one(model_with_fk)
    expected_serialized_obj = {
        'id': model_with_fk.id,
        'text': 'It was the best of times',
        'my_fk_id':  my_fk.id,
    }

    expect(serialized_obj).to.equal(expected_serialized_obj)


def test_serialize_one_with_datetime_field():
    from tests.models import (
        test_datetime_api,
        DateTimeModel)

    # When we delete all existing DateTimeModel objects
    DateTimeModel.objects.all().delete()

    # January 1, 1990
    new_years_1990 = datetime.datetime(1990, 1, 1)
    # Create an DateTimeModel object
    obj = DateTimeModel.objects.create(
        text='this is a datetime model',
        timestamp=new_years_1990)

    serialized_obj = test_datetime_api.serialize_one(obj)

    expected_serialized_obj = {
        'id': obj.id,
        'timestamp': new_years_1990.isoformat()
    }
    expect(serialized_obj).to.equal(expected_serialized_obj)


def test_create_record():
    from tests.models import (
        ExposedModelToSerialize,
        exposed_model_to_serialize_api)

    table_name = ExposedModelToSerialize._meta.db_table

    # When we delete all existing ExposedModelToSerialize objects
    ExposedModelToSerialize.objects.all().delete()

    _api = exposed_model_to_serialize_api
    record = _api.create_record(
        table_name,
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

    _api.create_record(
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


def test_delete_record():
    from tests.models import (
        ExposedModelToSerialize,
        exposed_model_to_serialize_api)

    table_name = ExposedModelToSerialize._meta.db_table

    # When we delete all existing ExposedModelToSerialize objects
    ExposedModelToSerialize.objects.all().delete()

    # and we create a record
    record = (ExposedModelToSerialize.objects
              .create(short_title='This is awesome',
                      author='Me'))

    # we expect Django ORM to return that there is now 1
    # record in this table
    (expect(ExposedModelToSerialize.objects
            .filter(id=record.id)
            .count())
     .to.equal(1))

    # Then through the restroom api we delete this record
    _api = exposed_model_to_serialize_api
    returned_data = _api.delete_record(table_name, record.id)

    # and expect nice success JSON
    expect(returned_data).to.equal({'status': 'deletion successful'})

    # and Django ORM to return that there are now 0 records
    # in this table
    (expect(ExposedModelToSerialize.objects
            .filter(id=record.id)
            .count())
     .to.equal(0))


def test_delete_nonexistent_record():
    from tests.models import (
        ExposedModelToSerialize,
        exposed_model_to_serialize_api)

    table_name = ExposedModelToSerialize._meta.db_table

    # When we delete all existing ExposedModelToSerialize objects
    ExposedModelToSerialize.objects.all().delete()

    _id = 1

    # we expect Django ORM to return that there is now 1
    # record in this table
    (expect(ExposedModelToSerialize.objects
            .filter(id=_id)
            .count())
     .to.equal(0))

    # Then through the restroom api we delete this record
    _api = exposed_model_to_serialize_api
    returned_data = _api.delete_record(table_name, _id)

    # and expect nice success JSON
    expected_data = {'error': 'no matching object found for id: 1'}
    expect(returned_data).to.equal(expected_data)

    # and Django ORM to return that there are now 0 records
    # in this table
    (expect(ExposedModelToSerialize.objects
            .filter(id=_id)
            .count())
     .to.equal(0))


def test_update_one():
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

    # Now we update and specify the fields
    # to be changed and their new values

    changes = {
        'short_title': 'This is a better short title',
    }

    serialized_data = (exposed_model_to_serialize_api
                       .update_one(table_name,
                                   _id,
                                   changes))

    expected_data = {
        'id': _id,
        'short_title': 'This is a better short title',
        'author': "Edgar Allen Poe",
    }

    # We should get back the expected serialized data
    expect(serialized_data).to.equal(expected_data)
    exposed_model_obj.delete()


def test_update_one_with_invalid_field():
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

    # Now we update and specify the fields
    # to be changed and their new values

    changes = {
        'an_invalid_field': 'This is a better short title',
    }

    serialized_data = (exposed_model_to_serialize_api
                       .update_one(table_name,
                                   _id,
                                   changes))

    expected_data = {
        "error": "cannot update inaccessible field 'an_invalid_field'"
    }

    # We should get back the expected serialized data
    expect(serialized_data).to.equal(expected_data)
    exposed_model_obj.delete()


def test_update_one_for_nonexistent_id():
    from tests.models import (
        ExposedModelToSerialize,
        exposed_model_to_serialize_api)

    table_name = ExposedModelToSerialize._meta.db_table

    # When we delete all existing ExposedModelToSerialize objects
    ExposedModelToSerialize.objects.all().delete()

    changes = {
        'short_title': 'This is the perfect title for a nonexistent object',
    }

    _id = 12345

    serialized_data = (exposed_model_to_serialize_api
                       .update_one(table_name,
                                   _id,
                                   changes))

    expected_data = {
        "error": "no matching object found for id: 12345"
    }

    # We should get back the expected serialized data
    expect(serialized_data).to.equal(expected_data)


def test_generate_single_item_view_for_GET_for_non_existent_item():
    from tests.models import (
        ExposedModelToSerialize,
        exposed_model_to_serialize_api)

    api = exposed_model_to_serialize_api
    table_name = ExposedModelToSerialize._meta.db_table

    # When we delete all existing ExposedModelToSerialize objects
    ExposedModelToSerialize.objects.all().delete()

    _id = 12345

    request = Mock(method='GET')
    response_from_GET = (api.generate_single_item_view(table_name)
                         .as_view()(request, _id))
    expected_response_json = {
        'error': 'no matching object found for id: {}'.format(_id)
    }
    response_json = ast.literal_eval(response_from_GET.content)
    expect(response_json).to.equal(expected_response_json)
    bad_response = HttpResponseBadRequest()
    expect(response_from_GET.status_code).to.equal(bad_response.status_code)

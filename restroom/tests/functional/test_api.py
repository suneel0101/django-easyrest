from restroom.models import MyModel
from restroom import API, api, expose
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
    (expect(restroom_api.table_model_map['restroom_mymodel'])
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
    (expect(restroom_api.table_model_map['restroom_mymodel'])
     .to.equal(expected_dict))


def test_expose_with_no_arguments():

    # When we decorate a Django Model with expose
    @expose()
    class ExposedModel(models.Model):
        title = models.CharField(max_length=150)
        active = models.BooleanField(default=False)

    table_name = ExposedModel._meta.db_table
    registered_value = api.table_model_map[table_name]

    expected_value = {
        'model': ExposedModel,
        'fields': ['id', 'title', 'active'],
        'allowed_methods': ['GET'],
    }
    # It registers it correctly with the Restroom API
    expect(registered_value).to.equal(expected_value)
    del api.table_model_map[table_name]


def test_expose_with_options():

    # When we decorate a Django Model with expose and
    # non-default options of allowable methods
    # and exposed fields
    @expose(allowed_methods=['GET', 'POST'], fields=['short_title', 'author'])
    class ExposedModelWithOptions(models.Model):
        short_title = models.CharField(max_length=150)
        expired = models.BooleanField(default=False)
        author = models.CharField(max_length=120)
        status = models.IntegerField(default=1)

    table_name = ExposedModelWithOptions._meta.db_table
    registered_value = api.table_model_map[table_name]

    expected_value = {
        'model': ExposedModelWithOptions,
        'fields': ['short_title', 'author'],
        'allowed_methods': ['GET', 'POST'],
    }

    # It should register it correctly with the Restroom API
    expect(registered_value).to.equal(expected_value)
    del registered_value


def test_retrieval_of_restroom_api():
    from restroom.models import ExposedModelToSerialize

    # When we delete all existing ExposedModelToSerialize objects
    ExposedModelToSerialize.objects.all().delete()

    # And we create an ExposedModelToSerialize object
    ExposedModelToSerialize.objects.create(
        short_title="This is a short title",
        author="Edgar Allen Poe",
    )

    # and retrieve this data from the database using the retrieve
    # method of the Restroom API
    serialized_data = api.retrieve('restroom_exposedmodeltoserialize')

    expected_data = [
        {
            'short_title': 'This is a short title',
            'author': "Edgar Allen Poe",
        },
    ]
    # We should get back the expected serialized data
    expect(serialized_data).to.equal(expected_data)

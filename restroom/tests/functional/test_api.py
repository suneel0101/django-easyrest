from restroom.tests.dummyapp.models import MyModel
from restroom import API
from sure import expect


def test_registering_a_model_adds_it_to_the_table_model_map():
    api = API()
    api.register(MyModel)
    expected_dict = {
        'model': MyModel,
        'fields': ['id', 'name'],
        'allowed_methods': ['GET'],
    }
    (expect([field.attname for field in MyModel._meta.fields])
     .to.equal(expected_dict['fields']))
    expect(api.table_model_map['dummyapp_mymodel']).to.equal(expected_dict)


def test_registering_with_non_default_options():
    api = API()
    api.register(MyModel,
                 {'allowed_methods': ['POST'],
                  'fields': ['name']})
    expected_dict = {
        'model': MyModel,
        'fields': ['name'],
        'allowed_methods': ['POST'],
    }
    expect(api.table_model_map['dummyapp_mymodel']).to.equal(expected_dict)

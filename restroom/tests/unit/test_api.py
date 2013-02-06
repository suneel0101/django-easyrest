from mock import Mock
from restroom import API


def test_registering_a_model_adds_it_to_the_table_model_map():
    model_class = Mock()
    model_class._meta.db_table = 'model_class_db_table'
    api = API()
    api.register(model_class)
    assert api.table_model_map['model_class_db_table'] == model_class

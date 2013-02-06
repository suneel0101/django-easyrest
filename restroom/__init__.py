from django.conf.urls import url, patterns
from collections import OrderedDict


class API(object):
    """
    This API will keep track of all of the Models that are
    registered to it.
    """
    default_configuration = {
        'allowed_methods': ['GET'],
    }

    def __init__(self):
        # map of table_name to model_data
        # such as `fields` to expose
        # and allowed_methods of calling the model resource
        self.table_model_map = OrderedDict()

    def register(self, model_class, options={}):
        """
        Registers a model_class with API along with the
        options that are passed in.

        >>> from myapp.models import MyModel
        >>> from restroom import api
        >>> api.register(MyModel, options={'fields': ['id', 'name']})

        However, this is not the recommended method registration.
        Instead, you should use the `expose` decorator.
        """
        model_data = self.get_model_data(model_class, options)
        self.table_model_map[model_class._meta.db_table] = model_data

    def get_model_data(self, model_class, options):
        """
        Gets the model_data from the model_class and options dictionary
        and defaults to the default_configuration when there is no
        other specification.
        """
        allowed_methods = (options.get('allowed_methods')
                           or self.default_configuration['allowed_methods'])
        fields = [field.attname for field in model_class._meta.fields]
        field_names = options.get('fields')
        if field_names:
            fields = [field for field in fields if field in field_names]

        return {
            'model': model_class,
            'fields': fields,
            'allowed_methods': allowed_methods,
        }

    def retrieve(self, table_name):
        """
        Given a table_name,
        This finds the model_data in self.table_model_map,
        queries the database, and returns the objects, serialized
        according to the fields specified.

        In apps/library/models.py
        ```
        from django.db import models
        from restroom import expose
        @expose(fields=['id', 'title', 'author'])
        class Book(models.Model)
            title = models.CharField(max_length=250)
            author = models.CharField(max_length=100)

        ```
        >>> from library.models import Book
        >>> Book.objects.create(title='My Book', author='Me')
        >>> from restroom import api
        >>> api.retrieve("library_book")
        [{"id": 1, "title": "My Book", "author": "Me"}]
        """
        model_data = self.table_model_map[table_name]
        model_class = model_data['model']
        fields = model_data['fields']
        return list(model_class.objects.values(*fields))

    @property
    def url_data(self):
        """
        Returns a list of dictionaries each containing url data,
        returned by self.get_url_data, for all of the models
        registered to the API
        """
        return [self.get_url_data(name, data)
         for name, data in self.table_model_map.items()]

    def get_url_data(self, table_name, model_data):
        """
        Given the table_name and corresponding model_data,
        which is found as a key, value pair in
        self.table_model_map
        """
        return {
            'regex': r'^{}/$'.format(table_name),
            'view': 'restroom.views.base',
            'name': '{}_api'.format(table_name),
        }

api = API()


def expose(api=api, **options):
    """
    This is the recommended way of exposing a model
    to be accessible via the Restroom's Restful API.

    Example 1:

    # limited to GET requests
    # all fields will be exposed in the data
    @expose()
    class My Model(models.Model):
        pass

    Example 2:

    # limited to GET and POST requests
    # only the id and name will be exposed in the data
    @expose(allowed_methods=['GET', 'POST'], fields=['id', name'])
    class Person(models.Model):
        name = models.CharField(max_length=100)
        is_active = models.BooleanField(default=False)
    """
    def expose_api(kls, api=api):
        api.register(kls, options)
        return kls
    return expose_api

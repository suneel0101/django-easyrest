from collections import OrderedDict
import simplejson as json

from django.conf.urls import url, patterns
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic.base import View

from .errors import RestroomError


class API(object):
    """
    This API will keep track of all of the Models that are
    registered to it.
    """
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
        return {
            'model': model_class,
            'allowed_methods': self.get_allowed_methods(
                options.get('allowed_methods')),
            'fields': self.get_exposed_fields(
                options.get('fields'), model_class),
        }

    def get_allowed_methods(self, optional_allowed_methods):
        if optional_allowed_methods:
            is_valid, offending_method = (self.validate_allowed_methods(
                    optional_allowed_methods))
            if not is_valid:
                message = "{} is not a valid allowable HTTP method".format(offending_method)
                raise RestroomError(message)
            allowed_methods = optional_allowed_methods
        else:
            allowed_methods = ['GET']
        return allowed_methods

    def get_exposed_fields(self, option_fields, model_class):
        model_fields = [field.attname for field in model_class._meta.fields]
        if option_fields:
            is_valid, offending_field = self.validate_fields(option_fields, model_fields)
            if not is_valid:
                message = "{} is not a valid field of {}".format(
                    offending_field,
                    model_class._meta.object_name)
                raise RestroomError(message)
            exposed_fields = [field for field in model_fields if field in option_fields]
        else:
            exposed_fields = model_fields
        return exposed_fields

    def validate_allowed_methods(self, option_allowed_methods):
        allowed_methods = ['GET', 'POST', 'PUT', 'DELETE']
        for method in option_allowed_methods:
            if method not in allowed_methods:
                return False, method
        return True, None

    def validate_fields(self, option_fields, model_fields):
        for option in option_fields:
            if option not in model_fields:
                return False, option
        return True, None

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

    def retrieve_one(self, table_name, _id):
        """
        This retrieves the record from table_name with id=_id.
        If not found, it returns an error dictionary.
        """
        model_data = self.table_model_map[table_name]
        model_class = model_data['model']
        fields = model_data['fields']
        try:
            obj = model_class.objects.get(id=_id)
        except model_class.DoesNotExist:
            return {'error': 'no matching object found for id: {}'.format(_id)}
        else:
            return self.serialize_one(obj)

    def serialize_one(self, model_instance):
        """
        Given a model instance (like a Person object from above),
        this returns the serialized object with only the fields
        as specified when registering it; defaults to all fields
        if no fields list is specified upon registration.
        """
        table_name = model_instance.__class__._meta.db_table
        model_data = self.table_model_map[table_name]
        fields = model_data['fields']
        return {field: getattr(model_instance, field) for field in fields}

    def create_record(self, table_name, object_data):
        """
        This creates a record in the `table_name` table
        with column values given by the object_data dictionary.

        Given the following model in app/people/models.py
        ```
        class Person(models.Model):
            name = models.CharField(max_length=150)
            is_awesome = models.BooleanField(default=True)
            age = models.PositiveIntegerField()
        ```

        api.create_record('people_person', {'name': 'James', 'age': 19})
        will create a Person object whose name is James, whose age is 19,
        and who is_awesome.
        """
        model_data = self.table_model_map[table_name]
        model_class = model_data['model']
        try:
            _object = model_class.objects.create(**object_data)
        except IntegrityError as e:
            return {'error': e.message}
        return self.serialize_one(_object)

    def delete_record(self, table_name, object_id):
        """
        This deletes a record from the `table_name` table
        with id=object_id
        """
        model_data = self.table_model_map[table_name]
        model_class = model_data['model']
        try:
            _object = model_class.objects.get(id=object_id)
        except model_class.DoesNotExist:
            error_message = ('no matching object found for id: {}'
                             .format(object_id))
            return {'error': error_message}

        try:
            _object.delete()
        except IntegrityError as e:
            return {'error': e.message}
        else:
            return {'status': 'deletion successful'}

    @property
    def url_patterns(self):
        """
        Returns urlpatterns for all of the registered models
        """
        return self.construct_url_patterns(self.url_data)

    @property
    def url_data(self):
        """
        Returns a list of dictionaries each containing url data,
        returned by self.get_url_data, for all of the models
        registered to the API
        """
        return [self.get_url_data(name, data)
         for name, data in self.table_model_map.items()]

    def construct_url_patterns(self, url_data_list):
        """
        Constructs the urlpatterns to be plugged into
        your urls.py, e.g.
        patterns('',
            url(r'^table_mymodel/$',
                'some.view.name',
                name='table_mymodel_api'),
            ...
        )

        """
        urls = []
        for data in url_data_list:
            urls.append(
                url(data['list_regex'],
                    data['list_view'],
                    name=data['list_name']))
            urls.append(
                url(data['single_item_regex'],
                    data['single_item_view'],
                    name=data['single_item_name']))
        return patterns('', *urls)

    def get_url_data(self, table_name, model_data):
        """
        Given the table_name and corresponding model_data,
        which is found as a key, value pair in
        self.table_model_map
        """
        return {
            "list_regex": r"^{}/$".format(table_name),
            "single_item_regex": r"^{}/(?P<_id>[\d]+)/$".format(table_name),
            "list_view": self.generate_list_view(table_name).as_view(),
            "single_item_view": (self.generate_single_item_view(table_name)
                                 .as_view()),
            "list_name": "{}_list_api".format(table_name),
            "single_item_name": "{}_single_item_api".format(table_name),
        }

    def generate_list_view(self, table_name):
        """
        Dynamically generates the Django view
        that will power the API endpoint for the model
        whose table_name is `table_name`

        Only GET requests are enabled currently, but
        POST, PUT and DELETE will be added, as well as
        such requests on /table_name/{id} for single item
        interactions.
        """
        model_data = self.table_model_map[table_name]
        allowed_methods = model_data['allowed_methods']
        api = self

        class RestroomListView(View):
            def get(self, request, *args, **kwargs):
                if 'GET' in allowed_methods:
                    data = api.retrieve(table_name)
                    return HttpResponse(
                        json.dumps(data),
                        mimetype='application/json')
                else:
                    return HttpResponseForbidden()

            def post(self, request, *args, **kwargs):
                if 'POST' in allowed_methods:
                    post_data = {k: v for k, v in request.POST.items()}
                    data = api.create_record(table_name, post_data)
                    return HttpResponse(
                        json.dumps(data),
                        mimetype='application/json')
                else:
                    return HttpResponseForbidden()

        return RestroomListView

    def generate_single_item_view(self, table_name):
        model_data = self.table_model_map[table_name]
        allowed_methods = model_data['allowed_methods']
        api = self

        class RestroomSingleItemView(View):
            def get(self, request, _id, *args, **kwargs):
                if 'GET' in allowed_methods:
                    data = api.retrieve_one(table_name, _id)
                    return HttpResponse(
                        json.dumps(data),
                        mimetype='application/json')
                else:
                    return HttpResponseForbidden()

            def delete(self, request, _id, *args, **kwargs):
                if 'DELETE' in allowed_methods:
                    data = api.delete_record(table_name, _id)
                    return HttpResponse(
                        json.dumps(data),
                        mimetype='application/json')
                else:
                    return HttpResponseForbidden()

        return RestroomSingleItemView

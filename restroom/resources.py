from django.db import IntegrityError
from .errors import RestroomValidationError
from .utils import get_val


class RestroomResource(object):
    def __init__(self, model, options={}):
        self.model = model
        self.http_methods = self.extract_http_methods(
            options.get('http_methods', ['GET']))
        self.field_map = self.extract_fields(options.get('fields', []))
        self.name = options.get('name', model._meta.db_table)

    def extract_http_methods(self, http_methods):
        invalid_http_methods = set(http_methods).difference(
            set(['GET', 'POST', 'PUT', 'DELETE']))
        if invalid_http_methods:
            raise RestroomValidationError(
                "The following are invalid HTTP methods: {}"
                .format(", ".join(invalid_http_methods)))
        return http_methods

    def extract_fields(self, field_names):
        model_fields = self.model._meta.fields
        get_field = lambda name: filter(lambda field: field.attname == name,
                                         model_fields)[0]
        if field_names:
            self.validate_fields(field_names)
            if 'id' not in field_names:
                field_names.append('id')
            return {name: get_field(name) for name in field_names}
        else:
            return {field.attname: field for field in model_fields}

    def validate_fields(self, field_names):
        model_field_names = map(lambda f: f.attname, self.model._meta.fields)
        invalid_field_names = (set(field_names)
                               .difference(set(model_field_names)))
        if invalid_field_names:
            message = ("Cannot resolve the following field names: {}"
                       .format(", ".join(invalid_field_names)))
            raise RestroomValidationError(message)

    def retrieve(self, filters=[]):
        qs = self.model.objects.all()
        if filters:
            try:
                self.validate_filters(filters)
            except RestroomValidationError as e:
                return self.get_error_message(e)
            qs = qs.filter(**self.get_filter_dict(filters))
        return {
            "items": list(qs.values(*self.field_map.keys()))
        }

    def get_filter_dict(self, filters):
        return {
            "{}__{}".format(
                _filter['field'],
                _filter["operator"]): _filter["value"]
            for _filter in filters}

    def validate_filters(self, filters):
            self.validate_filter_definition(filters)
            self.validate_fields([f["field"] for f in filters])
            self.validate_operators([f["operator"] for f in filters])

    def validate_operators(self, operators):
        valid_operators = ["contains", "icontains", "lt", "lte",
                           "gt", "gte", "exact", "in"]
        invalid_operators = set(operators).difference(set(valid_operators))
        if invalid_operators:
            raise RestroomValidationError(
                "The following are invalid filter operators: {}"
                .format(" ,".join(invalid_operators)))

    def validate_filter_definition(self, filters):
        for _filter in filters:
            keys = _filter.keys()
            if not ("field" in keys and
                    "operator" in keys and
                    "value" in keys):
                raise RestroomValidationError(
                    "Received a malformed filter")

    def get_object_by_id(self, _id):
        try:
            return {'object': self.model.objects.get(id=_id)}
        except self.model.DoesNotExist:
            return {'error': 'No result matches id: {}'.format(_id)}

    def retrieve_one(self, _id):
        data = self.get_object_by_id(_id)
        return self.serialize(data['object']) if data.get('object') else data

    def serialize(self, obj):
        return {name: get_val(obj, name) for name in self.field_map.keys()}

    def delete(self, _id):
        object_data = self.get_object_by_id(_id)
        if object_data.get('object'):
            object_data['object'].delete()
            return {}
        else:
            return object_data

    def create(self, data):
        if not data:
            return {"error": "no data was posted"}
        try:
            self.validate_fields(data.keys())
            _obj = self.model.objects.create(**data)
        except (RestroomValidationError, IntegrityError) as e:
            return self.get_error_message(e)
        else:
            return self.serialize(_obj)

    def update_one(self, _id, changes):
        try:
            self.validate_fields(changes.keys())
        except RestroomValidationError as e:
            return self.get_error_message(e)

        object_data = self.get_object_by_id(_id)
        if object_data.get('error'):
            return object_data
        _obj = object_data['object']

        for changed_attr, new_value in self.clean_changes(changes).iteritems():
            setattr(_obj, changed_attr, new_value)
        try:
            _obj.save()
        except IntegrityError as e:
            return self.get_error_message(e)
        return self.serialize(_obj)

    def clean_changes(self, changes):
        # remove `id` from change set if it is there
        if 'id' in changes.keys():
            del changes['id']
        return changes

    def update(self, filters, changes):
        try:
            self.validate_filters(filters)
            self.validate_fields(changes.keys())
        except RestroomValidationError as e:
            return self.get_error_message(e)

        try:
            objs = self.model.objects.filter(**self.get_filter_dict(filters))
            update_count = objs.update(**self.clean_changes(changes))
        except IntegrityError as e:
            return self.get_error_message(e)
        return {'update_count': update_count}

    def get_error_message(self, error):
        return {'error': error.message}

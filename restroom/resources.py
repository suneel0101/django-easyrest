from .errors import (
    RestroomInvalidFieldError,
    RestroomInvalidHTTPMethodError,
    RestroomInvalidOperatorError,
    RestroomMalformedFilterError)


class RestroomResource(object):
    def __init__(self, model, options={}):
        self.model = model
        self.http_methods = self.extract_http_methods(
            options.get('http_methods', ['GET']))
        self.field_map = self.extract_fields(options.get('fields', []))

    def extract_http_methods(self, http_methods):
        invalid_http_methods = set(http_methods).difference(
            set(['GET', 'POST', 'PUT', 'DELETE']))
        if invalid_http_methods:
            raise RestroomInvalidHTTPMethodError(
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
            message = ("Cannot resolve the following field names: {} "
                       .format(", ".join(invalid_field_names)))
            raise RestroomInvalidFieldError(message)

    def retrieve(self, filters=[]):
        qs = self.model.objects.all()
        if filters:
            self.validate_filter_definition(filters)
            self.validate_fields([f["field"] for f in filters])
            self.validate_operators([f["operator"] for f in filters])
            filter_dict = {
                "{}__{}".format(
                    _filter['field'],
                    _filter["operator"]): _filter["value"]
                for _filter in filters}
            qs = qs.filter(**filter_dict)
        return {
            'items': list(qs.values(*self.field_map.keys()))
        }

    def validate_operators(self, operators):
        valid_operators = ["contains", "icontains", "lt", "lte",
                           "gt", "gte", "exact", "in"]
        invalid_operators = set(operators).difference(set(valid_operators))
        if invalid_operators:
            raise RestroomInvalidOperatorError(
                "The following are invalid filter operators: {}"
                .format(" ,".join(invalid_operators)))

    def validate_filter_definition(self, filters):
        for _filter in filters:
            keys = _filter.keys()
            if not ("field" in keys and
                    "operator" in keys and
                    "value" in keys):
                raise RestroomMalformedFilterError(
                    "Received a malformed filter")

    def retrieve_one(self, _id):
        try:
            return {name: getattr(self.model.objects.get(id=_id), name)
                    for name in self.field_map.keys()}
        except self.model.DoesNotExist:
            return {'error': 'No result matches id: {}'.format(_id)}

    def delete(self, _id):
        try:
            self.model.objects.get(id=_id).delete()
        except self.model.DoesNotExist:
            return {'error': 'No result matches id: {}'.format(_id)}
        else:
            return {}

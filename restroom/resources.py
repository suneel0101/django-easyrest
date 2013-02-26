from .errors import (
    RestroomInvalidFieldError,
    RestroomInvalidHTTPMethodError)


class RestroomResource(object):
    def __init__(self, model, options={}):
        self.model = model
        self.http_methods = self.extract_http_methods(
            options.get('http_methods', ['GET']))
        self.field_map = self.extract_fields(model, options.get('fields', []))

    def extract_http_methods(self, http_methods):
        invalid_http_methods = set(http_methods).difference(
            set(['GET', 'POST', 'PUT', 'DELETE']))
        if invalid_http_methods:
            raise RestroomInvalidHTTPMethodError(
                "The following are invalid HTTP methods: {}"
                .format(", ".join(invalid_http_methods)))
        return http_methods

    def extract_fields(self, model, field_names):
        model_fields = model._meta.fields
        get_field = lambda name: filter(lambda field: field.attname == name,
                                         model_fields)[0]
        if field_names:
            self.validate_fields(model, field_names)
            if 'id' not in field_names:
                field_names.append('id')
            return {name: get_field(name) for name in field_names}
        else:
            return {field.attname: field for field in model_fields}

    def validate_fields(self, model, field_names):
        model_field_names = map(lambda f: f.attname, model._meta.fields)
        invalid_field_names = (set(field_names)
                               .difference(set(model_field_names)))
        if invalid_field_names:
            message = ("Cannot resolve the following field names: {} "
                       .format(", ".join(invalid_field_names)))
            raise RestroomInvalidFieldError(message)

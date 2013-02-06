class API(object):
    table_model_map = {}
    default_configuration = {
        'allowed_methods': ['GET'],
    }

    def register(self, model_class, options={}):
        allowed_methods = (options.get('allowed_methods')
                           or self.default_configuration['allowed_methods'])
        fields = [field.attname for field in model_class._meta.fields]
        field_names = options.get('fields')
        if field_names:
            fields = [field for field in fields if field in field_names]

        model_data = {
            'model': model_class,
            'fields': fields,
            'allowed_methods': allowed_methods,
        }
        self.table_model_map[model_class._meta.db_table] = model_data


api = API()


def expose(kls):
    api.register(kls)
    return kls

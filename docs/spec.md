```python
class RestroomAPI(object):
    def __init__(self):
        self.resources = []

    def register(self, model, options={}):
        self.resources.append(RestroomResource(model, options))

    def get_urls(self):
        urls = []
        for resource in self.resources:
            urls.extend([
                url(r"^{}/$".format(resource.name),
                    RestroomListView.as_view(resource=resource),
                    name="{}_list_api".format(resource.name)),
                url(r"^{}/(?P<_id>[\d]+)/$".format(resource.name),
                    RestroomSingleItemView.as_view(resource=resource),
                    name="{}_single_item_api".format(resource.name)),
            ])
        return patterns('', *urls)

class RestroomResource(object):
    def __init__(self, model, options):
        pass

    def validate_allowed_methods(self):
        pass

    def validate_fields(self):
        pass

    def retrieve(self, filters={}, page=None):
        pass

    def retrieve_one(self, _id):
        pass

    def create(self, data):
        pass

    def update(self, filters, changes):
        pass

    def update_one(self, _id, changes):
        pass

    def delete(self, _id):
        pass

    @property
    def key(self):
        pass

response_type = lambda data: HttpResponseBadRequest if data.get('error') else HttpResponse
response = lambda data: response_type(data)(json.dumps(data), mimetype='application/json')


class RestroomListView(View):
    def get(self, request, *args, **kwargs):
        if 'GET' in self.allowed_methods:
            filters = request.GET.get('filters', {})
            return response(self.resource.retrieve(filters=json.loads(filters),
                                                   page=request.GET.get('page')))
        return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        if 'POST' in self.allowed_methods:
            return response(self.resource.create(request.POST))
        return HttpResponseForbidden()

    def delete(self, request, *args, **kwargs):
        return HttpResponseForbidden()


class RestroomSingleItemView(View):
    def get(self, request, _id, *args, **kwargs):
        if 'GET' in self.allowed_methods:
            return response(self.resource.retrieve_one(_id))
        return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        return HttpResponseForbidden()

    def put(self, request, _id, *args, **kwargs):
        if 'PUT' in self.allowed_methods:
            # Hack because Django HttpRequest doesn't handle PUT well
            request.method = 'POST'
            return response(self.resource.update_one(_id, request.POST))
        return HttpResponseForbidden()

    def delete(self, request, _id, *args, **kwargs):
        if 'DELETE' in self.allowed_methods:
            return response(self.resource.delete_record(_id))
        return HttpResponseForbidden()

```


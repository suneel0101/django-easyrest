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

class RestroomListView(View):
    resource = None

    def get(self, request, *args, **kwargs):
        if 'GET' in self.resource.allowed_methods:
            retrieval_kwargs = {}
            filters = request.GET.get('filters')
            page = request.GET.get('page')
            if filters:
                filters = json.loads(filters)
                retrieval_kwargs['filters'] = filters
            if page:
                try:
                    retrieval_kwargs['page'] = int(page)
                except ValueError:
                    pass
            data = self.resource.retrieve(**retrieval_kwargs)
            return HttpResponse(
                json.dumps(data),
                mimetype='application/json')
        else:
            return HttpResponseForbidden()


```


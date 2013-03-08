import json
from django.http import (
    HttpResponse,
    HttpResponseForbidden)
from django.views.generic import View

from .constants import OK, CREATED, DELETED, BAD


def get_status(method):
    if method in ['POST', 'PUT']:
        return CREATED
    elif method == 'DELETE':
        return DELETED
    return OK


class BaseRestroomView(View):
    resource = None

    def get_response(self, data):
        status = BAD if 'error' in data else get_status(self.request.method)
        return HttpResponse(json.dumps(data), status=status,
                            mimetype='application/json')

    def dispatch(self, request, *args, **kwargs):
        if request.method not in self.resource.http_methods:
            return HttpResponseForbidden()
        return super(BaseRestroomView, self).dispatch(request, *args, **kwargs)


class RestroomListView(BaseRestroomView):
    def get(self, request, *args, **kwargs):
        filters = json.loads(request.GET.get('q', '[]'))
        return self.get_response(self.resource.retrieve(filters=filters))

    def post(self, request, *args, **kwargs):
        return self.get_response(self.resource.create(request.POST.dict()))

    def delete(self, request, *args, **kwargs):
        return HttpResponseForbidden()

    def put(self, request, *args, **kwargs):
        request.method = 'POST'
        filters = json.loads(request.POST.get('q', '[]'))
        changes = {k: v for k, v in request.POST.iteritems() if k != 'q'}
        return self.get_response(self.resource.update(filters, changes))


class RestroomItemView(BaseRestroomView):
    def get(self, request, _id, *args, **kwargs):
        return self.get_response(self.resource.retrieve_one(_id))

    def post(self, request, _id, *args, **kwargs):
        return HttpResponseForbidden()

    def delete(self, request, _id, *args, **kwargs):
        return self.get_response(self.resource.delete(_id))

    def put(self, request, _id, *args, **kwargs):
        request.method = 'POST'
        return self.get_response(
            self.resource.update_one(_id, request.POST.dict()))

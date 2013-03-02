import json

from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseBadRequest)
from django.views.generic import View


class BaseRestroomView(View):
    def get_response(self, data):
        response_type = HttpResponse
        if 'error' in data:
            response_type = HttpResponseBadRequest
        return response_type(json.dumps(data), mimetype='application/json')

    def dispatch(self, request, *args, **kwargs):
        if request.method not in self.resource.http_methods:
            return HttpResponseForbidden()
        return super(BaseRestroomView, self).dispatch(request, *args, **kwargs)


class RestroomListView(BaseRestroomView):
    resource = None

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

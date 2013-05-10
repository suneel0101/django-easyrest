import json
from django.http import (
    HttpResponse,
    HttpResponseForbidden)
from django.views.generic import View

from .constants import OK, CREATED, DELETED, BAD
from .utils import authorize


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
        if request.method != 'GET':
            return HttpResponseForbidden()
        request._user = None
        if self.resource.needs_auth:
            request._user = authorize(request)
            if not request._user:
                return HttpResponseForbidden()
        return super(BaseRestroomView, self).dispatch(request, *args, **kwargs)


class RestroomListView(BaseRestroomView):
    def get(self, request, *args, **kwargs):
        filters = json.loads(request.GET.get('q', '[]'))
        data = self.resource.retrieve(filters=filters, user=request._user)
        return self.get_response(data)


class RestroomItemView(BaseRestroomView):
    def get(self, request, _id, *args, **kwargs):
        data = self.resource.retrieve_one(_id, user=request._user)
        return self.get_response(data)

import json
from django.http import (
    HttpResponse,
    HttpResponseForbidden)
from django.views.generic import View

from .constants import OK, BAD


class BaseRestroomView(View):
    resource = None

    def get_response(self, data):
        status = BAD if 'error' in data else OK
        return HttpResponse(json.dumps(data), status=status,
                            mimetype='application/json')

    def dispatch(self, request, *args, **kwargs):
        if request.method != 'GET':
            return HttpResponseForbidden()
        request._user = None
        if self.resource.needs_authentication:
            request._user = self.resource.authorize(request)
            if not request._user:
                return HttpResponseForbidden()
        return super(BaseRestroomView, self).dispatch(request, *args, **kwargs)


class RestroomListView(BaseRestroomView):
    def get(self, request, *args, **kwargs):
        return self.get_response(self.resource.get_list(user=request._user))


class RestroomItemView(BaseRestroomView):
    def get(self, request, _id, *args, **kwargs):
        return self.get_response(self.resource.get_one(_id, request._user))

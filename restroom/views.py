import json

from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import View


class BaseRestroomView(View):
    def get_response(self, data):
        if self.http_method in self.resource.http_methods:
            return HttpResponse(json.dumps(data), mimetype="application/json")
        else:
            return HttpResponseForbidden()

    def dispatch(self, request, *args, **kwargs):
        self.http_method = request.method
        return super(BaseRestroomView, self).dispatch(request, *args, **kwargs)


class RestroomListView(BaseRestroomView):
    resource = None

    def get(self, request, *args, **kwargs):
        return self.get_response(self.resource.retrieve())

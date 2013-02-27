import json

from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import View

response = lambda data: HttpResponse(json.dumps(data),
                                     mimetype="application/json")
forbidden = HttpResponseForbidden


class RestroomMixin(object):
    def allowed(self, method):
        return method in self.resource.http_methods


class RestroomListView(View, RestroomMixin):
    resource = None

    def get(self, request, *args, **kwargs):
            return (response(self.resource.retrieve())
                    if self.allowed("GET") else forbidden())

import json

from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import View


class RestroomListView(View):
    resource = None

    def get(self, request, *args, **kwargs):
        if "GET" in self.resource.http_methods:
            return HttpResponse(
                json.dumps(self.resource.retrieve()),
                mimetype="application/json")
        else:
            return HttpResponseForbidden()

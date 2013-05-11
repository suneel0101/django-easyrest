import json
from django.http import (
    HttpResponse,
    HttpResponseForbidden)
from django.views.generic import View


class BaseAPIView(View):
    resource = None

    def get_response(self, data):
        status = 400 if 'error' in data else 200
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
        return super(BaseAPIView, self).dispatch(request, *args, **kwargs)


class ListView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        return self.get_response(self.resource.get_list(
                user=request._user,
                page=request.GET.get('page')))


class ItemView(BaseAPIView):
    def get(self, request, _id, *args, **kwargs):
        return self.get_response(self.resource.get_one(_id, request._user))


class SearchView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        return self.get_response(self.resource.search(request.GET.dict()))

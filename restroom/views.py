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
        request._user = None
        if self.resource.needs_auth:
            request._user = authorize(request)
            if not request._user:
                return HttpResponseForbidden()
        elif request.method not in self.resource.http_methods:
            return HttpResponseForbidden()
        return super(BaseRestroomView, self).dispatch(request, *args, **kwargs)


class RestroomListView(BaseRestroomView):
    def get(self, request, *args, **kwargs):
        filters = json.loads(request.GET.get('q', '[]'))
        data = self.resource.retrieve(filters=filters, user=request._user)
        return self.get_response(data)

    def post(self, request, *args, **kwargs):
        try:
            post_data = json.loads(request.raw_post_data)
        except ValueError:
            data = {"error": "malformed JSON POST data"}
        else:
            creation_data = post_data.get('data', {})
            if not creation_data:
                data = {"error": "invalid or empty POST data"}
            else:
                data = self.resource.create(creation_data)
        return self.get_response(data)

    def delete(self, request, *args, **kwargs):
        return HttpResponseForbidden()

    def put(self, request, *args, **kwargs):
        try:
            post_data = json.loads(request.raw_post_data)
        except ValueError:
            data = {"error": "malformed JSON POST data"}
        else:
            filters = post_data.get('q', [])
            changes = post_data.get('changes', {})
            if not changes:
                data = {"error": "invalid or empty POST data"}
            else:
                data = self.resource.update(filters, changes)
        return self.get_response(data)


class RestroomItemView(BaseRestroomView):
    def get(self, request, _id, *args, **kwargs):
        return self.get_response(self.resource.retrieve_one(_id))

    def post(self, request, _id, *args, **kwargs):
        return HttpResponseForbidden()

    def delete(self, request, _id, *args, **kwargs):
        return self.get_response(self.resource.delete(_id))

    def put(self, request, _id, *args, **kwargs):
        try:
            post_data = json.loads(request.raw_post_data)
        except ValueError:
            data = {"error": "malformed JSON POST data"}
        else:
            changes = post_data.get('changes', {})
            if not changes:
                data = {"error": "invalid or empty POST data"}
            else:
                data = self.resource.update_one(_id, changes)

        return self.get_response(data)

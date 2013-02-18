import simplejson as json

from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseBadRequest)
from django.views.generic.base import View


class RestroomListView(View):
    allowed_methods = ['GET']
    api = None
    table_name = None

    def get(self, request, *args, **kwargs):
        if 'GET' in self.allowed_methods:
            retrieval_kwargs = {}
            get_data = {k: v for k, v in request.GET.items()}
            filters = get_data.get('filters')
            page = get_data.get('page')
            if filters:
                filters = json.loads(filters)
                retrieval_kwargs['filters'] = filters
            if page:
                try:
                    retrieval_kwargs['page'] = int(page)
                except ValueError:
                    pass
            data = self.api.retrieve(self.table_name, **retrieval_kwargs)
            return HttpResponse(
                json.dumps(data),
                mimetype='application/json')
        else:
            return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        if 'POST' in self.allowed_methods:
            post_data = {k: v for k, v in request.POST.items()}
            data = self.api.create_record(self.table_name,
                                          post_data)
            return HttpResponse(
                json.dumps(data),
                mimetype='application/json')
        else:
            return HttpResponseForbidden()

    def delete(self, request, *args, **kwargs):
        return HttpResponseForbidden()


class RestroomSingleItemView(View):
    allowed_methods = ['GET']
    api = None
    table_name = None

    def get(self, request, _id, *args, **kwargs):
        if 'GET' in self.allowed_methods:
            data = self.api.retrieve_one(self.table_name, _id)
            if data.get('error'):
                response_type = HttpResponseBadRequest
            else:
                response_type = HttpResponse
            return response_type(
                json.dumps(data),
                mimetype='application/json')
        else:
            return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        return HttpResponseForbidden()

    def put(self, request, _id, *args, **kwargs):
        if 'PUT' in self.allowed_methods:
            put_data = {k: v for k, v in request.PUT.items()}
            data = self.api.update_one(self.table_name, _id, put_data)
            if data.get('error'):
                response_type = HttpResponseBadRequest
            else:
                response_type = HttpResponse
            return response_type(
                json.dumps(data),
                mimetype='application/json')
        else:
            return HttpResponseForbidden()

    def delete(self, request, _id, *args, **kwargs):
        if 'DELETE' in self.allowed_methods:
            data = self.api.delete_record(self.table_name, _id)
            if data.get('error'):
                response_type = HttpResponseBadRequest
            else:
                response_type = HttpResponse
            return response_type(
                json.dumps(data),
                mimetype='application/json')
        else:
            return HttpResponseForbidden()

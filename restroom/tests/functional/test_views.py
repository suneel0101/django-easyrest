import json
from django.http import QueryDict
from mock import Mock
from sure import expect, scenario
from restroom.views import RestroomListView
from restroom.resources import RestroomResource
from restroom.tests.models import Modelo

OK = 200
FORBIDDEN = 403
BAD = 400


def prepare_real_model(context):
    Modelo.objects.all().delete()

    Modelo.objects.create(
        text='Some text',
        optional_text='Optional text',
        slug='a-slug',
        awesome=True)

    Modelo.objects.create(
        text='Some more text',
        slug='b-slug',
        awesome=False)


@scenario(prepare_real_model)
def test_list_view_get(context):
    "default list view GET"
    request = Mock(method="GET")
    request.GET = QueryDict('')
    resource = RestroomResource(Modelo)
    response = RestroomListView.as_view(resource=resource)(request)
    expected_content = {"items": [{"id": 1,
                                   "text": "Some text",
                                   "optional_text": "Optional text",
                                   "slug": "a-slug",
                                   "awesome": True},
                                  {"id": 2,
                                   "text": "Some more text",
                                   "optional_text": "",
                                   "slug": "b-slug",
                                   "awesome": False}]}
    expect(json.loads(response.content)).to.equal(expected_content)


@scenario(prepare_real_model)
def test_list_view_get_with_nondefault_fields(context):
    "default list view GET with nondefault fields"
    request = Mock(method="GET")
    request.GET = QueryDict('')
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})
    response = RestroomListView.as_view(resource=resource)(request)
    expected_content = {"items": [{"id": 1,
                                   "text": "Some text",
                                   "slug": "a-slug",
                                   "awesome": True},
                                  {"id": 2,
                                   "text": "Some more text",
                                   "slug": "b-slug",
                                   "awesome": False}]}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(OK)


@scenario(prepare_real_model)
def test_list_view_get_when_get_not_allowed(context):
    "default list view GET when GET not allowed"
    request = Mock(method="GET")
    request.GET = QueryDict('')
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome'],
                                 'http_methods': ['POST']})
    response = RestroomListView.as_view(resource=resource)(request)
    expected_content = ""
    expect(response.content).to.equal(expected_content)
    expect(response.status_code).to.equal(FORBIDDEN)


@scenario(prepare_real_model)
def test_list_view_get_with_valid_filters(context):
    "default list view GET with valid filters"
    request = Mock(method="GET")
    query = ('[{"field": "id", "operator": "lt", "value": 2}'
        ',{"field": "text", "operator": "icontains", "value": "text"}]')

    request.GET = QueryDict('q={}'.format(query))
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome']})
    response = RestroomListView.as_view(resource=resource)(request)
    expected_content = {"items": [{"id": 1,
                                   "text": "Some text",
                                   "slug": "a-slug",
                                   "awesome": True}]}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(OK)


# @scenario(prepare_real_model)
# def test_list_view_get_with_invalid_filters(context):
#     "default list view GET with valid filters"
#     request = Mock(method="GET")
#     query = '[{"field": "id", "operator": "blah", "value": 2}]'
#     request.GET = QueryDict('q={}'.format(query))
#     resource = RestroomResource(Modelo,
#                                 {'fields': ['text', 'slug', 'awesome']})
#     response = RestroomListView.as_view(resource=resource)(request)
#     expected_content = {"error":
#                             "The following are invalid filter operators: blah"}
#     expect(json.loads(response.content)).to.equal(expected_content)
#     expect(response.status_code).to.equal(OK)

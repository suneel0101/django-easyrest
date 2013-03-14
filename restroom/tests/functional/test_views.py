import json
from django.http import QueryDict
from mock import Mock
from sure import expect, scenario
from restroom.views import (
    RestroomItemView)
from restroom.resources import RestroomResource
from restroom.tests.models import Modelo
from restroom.constants import OK, CREATED, DELETED, FORBIDDEN, BAD


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
def test_item_view_get_when_get_not_allowed(context):
    "default item view GET when GET not allowed"
    request = Mock(method="GET")
    request.GET = QueryDict('')
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome'],
                                 'http_methods': ['POST']})
    _id = 1
    response = RestroomItemView.as_view(resource=resource)(request, _id)
    expected_content = ""
    expect(response.content).to.equal(expected_content)
    expect(response.status_code).to.equal(FORBIDDEN)


@scenario(prepare_real_model)
def test_item_view_get_for_nonexistent_id(context):
    "default item view GET"
    request = Mock(method="GET")
    request.GET = QueryDict('')
    resource = RestroomResource(Modelo)
    _id = 5
    response = RestroomItemView.as_view(resource=resource)(request, _id)
    expected_content = {u'error': u'No result matches id: 5'}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_item_view_post_when_post_not_allowed(context):
    "ItemView POST when POST not allowed is forbidden"
    request = Mock(method="POST")
    request.POST = QueryDict('')
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome'],
                                 'http_methods': ['PUT']})
    _id = 1
    response = RestroomItemView.as_view(resource=resource)(request, _id)
    expected_content = ""
    expect(response.content).to.equal(expected_content)
    expect(response.status_code).to.equal(FORBIDDEN)


@scenario(prepare_real_model)
def test_item_view_post_when_post_allowed_still_forbidden(context):
    "ItemView POST when POST allowed is still forbidden"
    request = Mock(method="POST")
    request.POST = QueryDict('')
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome'],
                                 'http_methods': ['POST']})
    _id = 1
    response = RestroomItemView.as_view(resource=resource)(request, _id)
    expected_content = ""
    expect(response.content).to.equal(expected_content)
    expect(response.status_code).to.equal(FORBIDDEN)


@scenario(prepare_real_model)
def test_item_view_delete(context):
    "default item view DELETE"
    request = Mock(method="DELETE")
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome'],
                                 'http_methods': ['DELETE']})
    _id = 1
    response = RestroomItemView.as_view(resource=resource)(request, _id)
    expected_content = {}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(DELETED)


@scenario(prepare_real_model)
def test_item_view_delete_for_nonexistent_id(context):
    "ItemView DELETE for nonexistent ID"
    request = Mock(method="DELETE")
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome'],
                                 'http_methods': ['DELETE']})
    _id = 7
    response = RestroomItemView.as_view(resource=resource)(request, _id)
    expected_content = {u'error': u'No result matches id: 7'}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_item_view_delete_when_not_allowed(context):
    "ItemView DELETE when not allowed returns forbidden"
    request = Mock(method="DELETE")
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome'],
                                 'http_methods': ['GET']})
    _id = 1
    response = RestroomItemView.as_view(resource=resource)(request, _id)
    expected_content = ""
    expect(response.content).to.equal(expected_content)
    expect(response.status_code).to.equal(FORBIDDEN)


@scenario(prepare_real_model)
def test_item_put_with_valid_changes(context):
    "ItemView PUT with valid changes"
    request = Mock(method="PUT")
    _id = 1
    request.POST = QueryDict('text=baller')
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome'],
                                 'http_methods': ['PUT']},)
    response = RestroomItemView.as_view(resource=resource)(request, _id)
    expected_content = {"id": 1,
                        "text": "baller",
                        "awesome": True,
                        "slug": "a-slug"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(CREATED)


@scenario(prepare_real_model)
def test_item_put_with_valid_changes_but_nonexistent_id(context):
    "ItemView PUT with valid changes but nonexistent ID"
    request = Mock(method="PUT")
    _id = 9
    request.POST = QueryDict('text=baller')
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome'],
                                 'http_methods': ['PUT']},)
    response = RestroomItemView.as_view(resource=resource)(request, _id)
    expected_content = {u'error': u'No result matches id: 9'}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_item_put_with_invalid_change_field(context):
    "ItemView PUT with invalid change field"
    request = Mock(method="PUT")
    _id = 1
    request.POST = QueryDict('blah=bloop')
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome'],
                                 'http_methods': ['PUT']},)
    response = RestroomItemView.as_view(resource=resource)(request, _id)
    expected_content = {
        "error": "Cannot resolve the following field names: blah"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_item_put_with_failure_at_model_level(context):
    "ItemView PUT response when failure occurs at model level"
    request = Mock(method="PUT")
    request.POST = QueryDict('slug=a-slug')
    _id = 2
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome'],
                                 'http_methods': ['PUT']},)
    response = RestroomItemView.as_view(resource=resource)(request, _id)
    expected_content = {
        "error": "column slug is not unique"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_item_view_put_when_not_allowed(context):
    "ItemView PUT when not allowed returns forbidden"
    request = Mock(method="PUT")
    resource = RestroomResource(Modelo,
                                {'fields': ['text', 'slug', 'awesome'],
                                 'http_methods': ['GET']})
    _id = 1
    response = RestroomItemView.as_view(resource=resource)(request, _id)
    expected_content = ""
    expect(response.content).to.equal(expected_content)
    expect(response.status_code).to.equal(FORBIDDEN)

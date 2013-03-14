import json
from sure import expect, scenario

from django.test.client import Client
from django.core.urlresolvers import reverse
from restroom.tests.functional.test_views import prepare_real_model
from restroom.constants import OK, CREATED, DELETED, FORBIDDEN, BAD

client = Client()


@scenario(prepare_real_model)
def test_list_endpoint_simple_get(context):
    "Simple GET to list endpoint"
    response = client.get(reverse('tests_modelo_list'))
    expect(json.loads(response.content)).to.equal(
        {"items": [{"id": 1,
                    "text": "Some text",
                    "slug": "a-slug",
                    "awesome": True},
                   {"id": 2,
                    "text": "Some more text",
                    "slug": "b-slug",
                    "awesome": False}]})
    expect(response.status_code).to.equal(OK)


@scenario(prepare_real_model)
def test_list_endpoint_get_with_filters(context):
    "GET to list endpoint with filters"
    query = ('[{"field": "id", "operator": "lt", "value": 2}'
             ',{"field": "text", "operator": "icontains", "value": "text"}]')
    response = client.get(reverse('tests_modelo_list'),
                          data={'q': query})
    expect(json.loads(response.content)).to.equal(
        {"items": [{"id": 1,
                    "text": "Some text",
                    "slug": "a-slug",
                    "awesome": True}]})
    expect(response.status_code).to.equal(OK)


@scenario(prepare_real_model)
def test_list_endpoint_get_with_invalid_filters(context):
    "GET to list endpoint with invalid filters"
    query = '[{"field": "id", "operator": "blah", "value": 2}]'
    response = client.get(reverse('tests_modelo_list'),
                          data={'q': query})
    expected_content = {
        "error": "The following are invalid filter operators: blah"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_list_view_post(context):
    "POST to list endpoint with valid fields and values"
    data = '{"text": "posted text", "slug": "posted-slug", "awesome": 0}'
    url = reverse('tests_modelo_list')
    response = client.post(url, data={'data': data})
    expected_content = {
        "id": 3,
        "text": 'posted text',
        "slug": 'posted-slug',
        "awesome": 0}

    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(CREATED)


@scenario(prepare_real_model)
def test_list_view_post_with_no_data(context):
    "POST to list endpoint with valid fields and values"
    url = reverse('tests_modelo_list')
    response = client.post(url)
    expected_content = {"error": "no data was posted"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)

import json
from sure import expect, scenario

from django.test.client import Client
from django.core.urlresolvers import reverse
from restroom.tests.models import Modelb
from restroom.tests.functional.test_views import prepare_real_model
from restroom.constants import OK, CREATED, DELETED, FORBIDDEN, BAD

client = Client()


def prepare_real_modelb(context):
    Modelb.objects.all().delete()

    Modelb.objects.create(
        text='Some text',
        optional_text='Optional text',
        slug='a-slug',
        awesome=True)

    Modelb.objects.create(
        text='Some more text',
        slug='b-slug',
        awesome=False)


@scenario(prepare_real_model)
def test_list_endpoint_simple_get(context):
    "Simple GET to list endpoint"
    response = client.get(reverse('tests_modelo_list'),
                          content_type='application/json')
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
                          data={'q': query},
                          content_type='application/json')
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
                          data={'q': query},
                          content_type='application/json')
    expected_content = {
        "error": "The following are invalid filter operators: blah"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_list_view_post(context):
    "POST to list endpoint with valid fields and values"
    data = '{"data": {"text": "posted text", "slug": "posted-slug", "awesome": 0}}'
    url = reverse('tests_modelo_list')
    response = client.post(url,
                           data=data,
                           content_type='application/json')
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
    expected_content = {"error": "malformed JSON POST data"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_list_view_post_with_invalid_fields(context):
    "POST to list endpoint with invalid fields"
    data = json.dumps({"data": {'strangefield': 'posted text',
                       'slug': 'posted-slug',
                       'awesome': True}})
    url = reverse('tests_modelo_list')
    response = client.post(url,
                           data,
                           content_type='application/json')
    expected_content = {
        "error": "Cannot resolve the following field names: strangefield"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_list_view_post_with_model_level_failure(context):
    "POST to list endpoint with model leve failure"
    data = json.dumps({"data": {'text': 'posted text',
                       'slug': 'a-slug',
                       'awesome': True}})
    url = reverse('tests_modelo_list')
    response = client.post(url,
                           data,
                           content_type='application/json')
    expected_content = {
        'error': 'column slug is not unique'}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_list_view_put_forbidden_when_not_allowed(context):
    "List PUT when not allowed is forbidden"
    url = reverse('tests_modelo_list')
    response = client.put(url, content_type='application/json')
    expect(response.status_code).to.equal(FORBIDDEN)
    expect(response.content).to.equal("")


@scenario(prepare_real_model)
def test_list_view_delete_forbidden_when_not_allowed(context):
    "List DELETE when not allowed is forbidden"
    url = reverse('tests_modelo_list')
    response = client.delete(url, content_type='application/json')
    expect(response.status_code).to.equal(FORBIDDEN)
    expect(response.content).to.equal("")


@scenario(prepare_real_model)
def test_list_view_delete_forbidden_even_when_allowed(context):
    "List DELETE even when allowed is still forbidden"
    url = reverse('tests_modelc_list')
    response = client.delete(url)
    expect(response.status_code).to.equal(FORBIDDEN)
    expect(response.content).to.equal("")


@scenario(prepare_real_modelb)
def test_list_put_with_valid_filters(context):
    "PUT to list with valid filters and changes"
    query = [
        {"field": "id", "operator": "in", "value": [1]},
        {"field": "text", "operator": "icontains", "value": "text"},
    ]
    changes = {'text': 'baller text'}
    PUT_data = json.dumps({"q": query, "changes": changes})
    url = reverse('tests_modelb_list')
    response = client.put(url,
                          PUT_data,
                          content_type='application/json')
    expect(response.status_code).to.equal(CREATED)
    expect(json.loads(response.content)).to.equal({"update_count": 1})


@scenario(prepare_real_modelb)
def test_list_put_with_invalid_changefield(context):
    "PUT to list with invalid change fields"
    query = [
        {"field": "id", "operator": "in", "value": [1, 2]},
        {"field": "text", "operator": "icontains", "value": "text"},
    ]
    changes = {'invalidfield': 'honey badger'}
    PUT_data = json.dumps({"q": query, "changes": changes})
    url = reverse('tests_modelb_list')
    response = client.put(url,
                          PUT_data,
                          content_type='application/json')
    expect(response.status_code).to.equal(BAD)
    expect(json.loads(response.content)).to.equal(
        {"error": "Cannot resolve the following field names: invalidfield"})


@scenario(prepare_real_model)
def test_list_put_with_invalid_filter(context):
    "PUT with invalid filters should return error JSON"
    query = [{"field": "crazy", "operator": "lt", "value": [1, 2]}]
    changes = {"text": "great text"}
    PUT_data = json.dumps({"q": query, "changes": changes})
    url = reverse('tests_modelb_list')
    response = client.put(url,
                          PUT_data,
                          content_type='application/json')
    expected_content = {
        "error": "Cannot resolve the following field names: crazy"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_put_with_failure_at_model_level(context):
    "Test PUT response when failure occurs at model level"
    query = [{"field": "id", "operator": "lt", "value": 4}]
    changes = {"slug": "a-slug"}
    PUT_data = json.dumps({"q": query, "changes": changes})
    url = reverse('tests_modelb_list')
    response = client.put(url,
                          PUT_data,
                          content_type='application/json')
    expected_content = {
        "error": "column slug is not unique"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)

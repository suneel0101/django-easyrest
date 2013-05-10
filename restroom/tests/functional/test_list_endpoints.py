import json
from sure import expect, scenario

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from restroom.tests.models import ModelForUser
from restroom.tests.utils import (
    prepare_real_model,
    prepare_real_modelb,
    prepare_real_model_authed,
    prepare_real_model_fk,
    prepare_real_model_fk_id,
    prepare_api_key,
    prepare_real_model_m2m)
from restroom.constants import OK, CREATED, FORBIDDEN, BAD

client = Client()


@scenario(prepare_real_model_authed)
def test_list_endpoint_authed_get_forbidden(context):
    "GET to authed by unauthed is Forbidden"
    response = client.get(reverse('tests_modelauthed_list'),
                          content_type='application/json')
    expect(response.content).to.equal('')
    expect(response.status_code).to.equal(FORBIDDEN)


@scenario(prepare_api_key)
def test_list_endpoint_authed_only_for_user(context):
    "GET to authed by authed user for only_for_user works"
    ModelForUser.objects.all().delete()
    user = User.objects.create_user('new_user', 'abc@gmail.com', '1234')
    ModelForUser.objects.create(text='coo',
                                slug='coo-slug',
                                awesome=False,
                                owner=user)
    ModelForUser.objects.create(text='cooler',
                                slug='cooler-slug',
                                awesome=True,
                                owner=context.user)
    api_key = context.api_key
    response = client.get(reverse('tests_modelforuser_list'),
                          content_type='application/json',
                          **{'RESTROOM_API_KEY': api_key.token})
    expect(json.loads(response.content)).to.equal(
        {"items": [{"id": 2,
                    "text": "cooler",
                    "optional_text": "",
                    "slug": "cooler-slug",
                    "owner_id": context.user.id,
                    "awesome": True}]})
    expect(response.status_code).to.equal(OK)
    expect(context.user.is_superuser).to.equal(False)
    ModelForUser.objects.all().delete()
    user.delete()


@scenario(prepare_api_key)
def test_put_list_endpoint_authed_only_for_user(context):
    "PUT to authed by authed user for only_for_user works"
    ModelForUser.objects.all().delete()
    user = User.objects.create_user('new_user', 'abc@gmail.com', '1234')
    ModelForUser.objects.create(text='coo',
                                slug='coo-slug',
                                awesome=False,
                                owner=user)
    ModelForUser.objects.create(text='cooler',
                                slug='cooler-slug',
                                awesome=True,
                                owner=context.user)
    api_key = context.api_key
    changes = {'text': 'baller text'}
    data = json.dumps({"changes": changes})
    response = client.put(reverse('tests_modelforuser_list'),
                          data,
                          content_type='application/json',
                          **{'RESTROOM_API_KEY': api_key.token})
    expect(json.loads(response.content)).to.equal(
        {"update_count": 1})
    model_for_context_user = ModelForUser.objects.get(id=2)
    expect(model_for_context_user.text).to.equal('baller text')
    expect(response.status_code).to.equal(CREATED)
    expect(context.user.is_superuser).to.equal(False)
    ModelForUser.objects.all().delete()
    user.delete()


@scenario([prepare_real_model_authed, prepare_api_key])
def test_list_endpoint_authed_get_works(context):
    "GET to authed by authed user works"
    api_key = context.api_key
    response = client.get(reverse('tests_modelauthed_list'),
                          content_type='application/json',
                          **{'RESTROOM_API_KEY': api_key.token})
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


@scenario(prepare_real_model_fk)
def test_list_endpoint_get_with_foreign_key(context):
    "GET to resource with foreign key returns correctly serialized data"
    response = client.get(reverse('tests_modelfk_list'),
                          content_type='application/json')
    expect(json.loads(response.content)).to.equal(
        {"items": [{"id": 1,
                    "text": "Some text",
                    "slug": "a-slug",
                    "awesome": True,
                    "foreign": 1},
                   {"id": 2,
                    "text": "Some more text",
                    "slug": "b-slug",
                    "awesome": False,
                    "foreign": 2}]
         })
    expect(response.status_code).to.equal(OK)


@scenario(prepare_real_model_m2m)
def test_list_endpoint_get_with_m2m(context):
    "GET to resource with m2m returns correctly serialized data"
    response = client.get(reverse('tests_modelm2m_list'),
                          content_type='application/json')
    expect(json.loads(response.content)).to.equal(
        {"items": [{"id": 1, "text": "awesome m2m"}]})
    expect(response.status_code).to.equal(OK)


@scenario(prepare_real_model_fk_id)
def test_list_endpoint_get_with_foreign_key_registered_with__id(context):
    "GET to resource works right when fk is registered with default `.._id`"
    response = client.get(reverse('tests_modelfkid_list'),
                          content_type='application/json')
    expect(json.loads(response.content)).to.equal(
        {"items": [{"id": 1,
                    "text": "Some text",
                    "optional_text": "Optional text",
                    "slug": "a-slug",
                    "awesome": True,
                    "foreign_id": 1},
                   {"id": 2,
                    "text": "Some more text",
                    "optional_text": "",
                    "slug": "b-slug",
                    "awesome": False,
                    "foreign_id": 2}]
         })
    expect(response.status_code).to.equal(OK)


@scenario(prepare_real_modelb)
def test_list_endpoint_simple_get_with_datetime(context):
    "Simple GET to list endpoint with DateTime"
    response = client.get(reverse('tests_modelb_list'),
                          content_type='application/json')
    expect(json.loads(response.content)).to.equal(
        {"items": [{"id": 1,
                    "text": "Some text",
                    'timestamp': '2013-01-01T12:00:00',
                    "slug": "a-slug",
                    "awesome": True},
                   {"id": 2,
                    "text": "Some more text",
                    'timestamp': '2013-03-01T12:00:00',
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
def test_list_view_post_without_data(context):
    "POST to list endpoint with no data being passed into post"
    url = reverse('tests_modelo_list')
    response = client.post(url, content_type='application/json')
    expected_content = {"error": "invalid or empty POST data"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_list_view_post_with_malformed_json(context):
    "POST to list endpoint with malformed data"
    url = reverse('tests_modelo_list')
    response = client.post(url,
                           "blahblah",
                           content_type='application/json')
    expected_content = {"error": "malformed JSON POST data"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_list_view_put_with_no_data(context):
    "PUT to list endpoint with no data being passed into put"
    url = reverse('tests_modelb_list')
    response = client.put(url, content_type='application/json')
    expected_content = {"error": "invalid or empty POST data"}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_list_view_put_with_malformed_data(context):
    "PUT to list endpoint with malformed data"
    url = reverse('tests_modelb_list')
    response = client.put(url,
                          "blahblah",
                          content_type='application/json')
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
    "POST to list endpoint with model level failure"
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
def test_list_view_get_forbidden_when_not_allowed(context):
    "List GET when not allowed is forbidden"
    url = reverse('tests_modela_list')
    response = client.get(url, content_type='application/json')
    expect(response.status_code).to.equal(FORBIDDEN)
    expect(response.content).to.equal("")


@scenario(prepare_real_model)
def test_list_view_post_forbidden_when_not_allowed(context):
    "List POST when not allowed is forbidden"
    url = reverse('tests_modelc_list')
    response = client.post(url, content_type='application/json')
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

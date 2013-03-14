import json
from sure import expect, scenario

from django.test.client import Client
from django.core.urlresolvers import reverse
from restroom.tests.utils import (prepare_real_model,
                                  prepare_real_modelb,
                                  prepare_real_modelc)
from restroom.constants import OK, CREATED, DELETED, FORBIDDEN, BAD

client = Client()


@scenario(prepare_real_model)
def test_item_endpoint_get(context):
    "GET item"
    response = client.get(reverse('tests_modelo_item', kwargs={'_id': 1}),
                          content_type='application/json')
    expect(json.loads(response.content)).to.equal({"id": 1,
                                                   "text": "Some text",
                                                   "slug": "a-slug",
                                                   "awesome": True})
    expect(response.status_code).to.equal(OK)


@scenario(prepare_real_model)
def test_item_endpoint_get_for_nonexistent_id(context):
    "GET nonexistent item"
    response = client.get(reverse('tests_modelo_item', kwargs={'_id': 5}),
                          content_type='application/json')
    expected_content = {u'error': u'No result matches id: 5'}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_item_endpoint_get_when_not_allowed(context):
    "GET item not allowed returns forbidden"
    response = client.get(reverse('tests_modelc_item', kwargs={'_id': 5}),
                          content_type='application/json')
    expected_content = ''
    expect(response.content).to.equal(expected_content)
    expect(response.status_code).to.equal(FORBIDDEN)


@scenario(prepare_real_model)
def test_item_endpoint_post_when_not_allowed(context):
    "POST item not allowed returns forbidden"
    response = client.post(reverse('tests_modelb_item',
                                   kwargs={'_id': 1}),
                           content_type='application/json')
    expected_content = ''
    expect(response.content).to.equal(expected_content)
    expect(response.status_code).to.equal(FORBIDDEN)


@scenario(prepare_real_model)
def test_item_endpoint_post_when_allowed(context):
    "POST item even when allowed still returns forbidden"
    response = client.post(reverse('tests_modela_item',
                                   kwargs={'_id': 1}),
                           content_type='application/json')
    expected_content = ''
    expect(response.content).to.equal(expected_content)
    expect(response.status_code).to.equal(FORBIDDEN)


@scenario(prepare_real_modelc)
def test_item_endpoint_delete(context):
    "DELETE item"
    response = client.delete(reverse('tests_modelc_item', kwargs={'_id': 1}),
                             content_type='application/json')
    expected_content = ''
    expect(response.content).to.equal(expected_content)
    expect(response.status_code).to.equal(DELETED)


@scenario(prepare_real_modelc)
def test_item_endpoint_delete_nonexistent_id(context):
    "DELETE nonexistent item"
    response = client.delete(reverse('tests_modelc_item', kwargs={'_id': 7}),
                             content_type='application/json')
    expected_content = {u'error': u'No result matches id: 7'}
    expect(json.loads(response.content)).to.equal(expected_content)
    expect(response.status_code).to.equal(BAD)


@scenario(prepare_real_model)
def test_item_endpoint_delete_not_allowed(context):
    "DELETE item when not allowed returns forbidden"
    response = client.delete(reverse('tests_modela_item',
                                     kwargs={'_id': 1}),
                             content_type='application/json')
    expected_content = ''
    expect(response.content).to.equal(expected_content)
    expect(response.status_code).to.equal(FORBIDDEN)

import json
from sure import expect, scenario

from django.core.urlresolvers import reverse
from django.test.client import Client

from app.models import Item

client = Client()


def create_items(context):
    # Delete all items
    Item.objects.all().delete()
    # Create 30 items
    for x in range(30):
        Item.objects.create(
            name="my name is {}".format(x),
            text="my text is {}".format(x),
            is_active=x % 2,
            status=x)


@scenario(create_items)
def test_get_list(context):
    response = client.get(reverse('item_list'),
                          content_type='application/json')

    expected_response_content = {
        "items": [
            {
                "id": x + 1,
                "text": "my text is {}".format(x),
                "popularity": x + int(x % 2),
            } for x in range(30)]}
    expect(json.loads(response.content)).to.equal(expected_response_content)
    expect(response.status_code).to.equal(200)


@scenario(create_items)
def test_get_list_reverse_order(context):
    response = client.get(reverse('reverse_order_item_list'),
                          content_type='application/json')

    expected_response_content = {
        "items": [
            {
                "id": x + 1,
                "text": "my text is {}".format(x),
                "popularity": x + int(x % 2),
            } for x in reversed(range(30))]}
    expect(json.loads(response.content)).to.equal(expected_response_content)
    expect(response.status_code).to.equal(200)


@scenario(create_items)
def test_get_list_paginated(context):
    response = client.get(reverse('paginated_item_list'),
                          content_type='application/json')

    expected_response_content = {
        "items": [
            {
                "id": x + 1,
                "text": "my text is {}".format(x),
                "popularity": x + int(x % 2),
            } for x in range(20)]}
    expect(json.loads(response.content)).to.equal(expected_response_content)
    expect(response.status_code).to.equal(200)

    response_page_2 = client.get(reverse('paginated_item_list'),
                                 data={'page': 2},
                          content_type='application/json')

    expected_response_page_2_content = {
        "items": [
            {
                "id": x + 1,
                "text": "my text is {}".format(x),
                "popularity": x + int(x % 2),
            } for x in range(20, 30)]}
    expect(json.loads(response_page_2.content)).to.equal(
        expected_response_page_2_content)
    expect(response_page_2.status_code).to.equal(200)

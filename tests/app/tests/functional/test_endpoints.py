import json
from sure import expect, scenario

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client

from easyrest.models import APIKey
from app.models import Item, UserItem

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


def test_get_list_failed_authentication_without_key():
    APIKey.objects.all().delete()
    response = client.get(reverse('authorized_item_list'),
                          content_type='application/json')
    expect(response.status_code).to.equal(403)


def test_get_list_failed_authentication_with_wrong_key():
    APIKey.objects.all().delete()
    response = client.get(reverse('authorized_item_list'),
                          data={'key': "the-wrong-key"},
                          content_type='application/json')
    expect(response.status_code).to.equal(403)


def test_get_list_successful_authentication():
    # Delete all items
    UserItem.objects.all().delete()
    APIKey.objects.all().delete()
    User.objects.all().delete()
    user = User.objects.create(username='tester', password='123')
    user2 = User.objects.create(username='tester2', password='345')

    # Create 30 items
    for x in range(30):
        UserItem.objects.create(
            name="my name is {}".format(x),
            user=[user, user2][x % 2],
            is_active=x % 2)

    apikey = APIKey.objects.create(user=user)
    response = client.get(reverse('authorized_item_list'),
                          data={'apikey': apikey.token},
                          content_type='application/json')
    expected_response_content = {
        "items": [
            {
                "id": x + 1,
                "name": "my name is {}".format(x),
                "user_id": [user.id, user2.id][x % 2],
            } for x in range(30)]}
    expect(json.loads(response.content)).to.equal(expected_response_content)
    expect(response.status_code).to.equal(200)


def test_get_list_filter_by_user():
    # Delete all items
    UserItem.objects.all().delete()
    APIKey.objects.all().delete()
    User.objects.all().delete()
    user = User.objects.create(username='tester', password='123')
    user2 = User.objects.create(username='tester2', password='345')

    # Create 30 items
    for x in range(30):
        UserItem.objects.create(
            name="my name is {}".format(x),
            user=[user, user2][x % 2],
            is_active=x % 2)

    apikey = APIKey.objects.create(user=user)
    response = client.get(reverse('by_user_authorized_item_list'),
                          data={'apikey': apikey.token},
                          content_type='application/json')
    all_items = [
            {
                "id": x + 1,
                "name": "my name is {}".format(x),
                "user_id": [user.id, user2.id][x % 2],
            } for x in range(30)]

    expected_items = [item for item in all_items if item["user_id"] == user.id]
    expected_response_content = {
        "items": expected_items}
    expect(json.loads(response.content)).to.equal(expected_response_content)
    expect(response.status_code).to.equal(200)


def test_get_list_with_non_GET_method():
    response = client.post(reverse('item_list'),
                          content_type='application/json')
    expect(response.status_code).to.equal(403)

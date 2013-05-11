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
def test_get_item(context):
    response = client.get(reverse('item_item', kwargs={"_id": 1}),
                          content_type='application/json')

    expected_response_content = {
        "id": 1,
        "text": "my text is 0",
        "popularity": 0}
    expect(json.loads(response.content)).to.equal(expected_response_content)
    expect(response.status_code).to.equal(200)


@scenario(create_items)
def test_get_non_existent_item(context):
    response = client.get(reverse('item_item', kwargs={"_id": 99}),
                          content_type='application/json')

    expected_response_content = {"error": "No result matches id: 99"}
    expect(json.loads(response.content)).to.equal(expected_response_content)
    expect(response.status_code).to.equal(400)


def test_get_item_failed_authentication_without_key():
    APIKey.objects.all().delete()
    response = client.get(reverse('authorized_item_item', kwargs={"_id": 1}),
                          content_type='application/json')
    expect(response.status_code).to.equal(403)


def test_get_item_failed_authentication_with_wrong_key():
    APIKey.objects.all().delete()
    response = client.get(reverse('authorized_item_item', kwargs={"_id": 1}),
                          data={'key': "the-wrong-key"},
                          content_type='application/json')
    expect(response.status_code).to.equal(403)


def test_get_item_authed_successful():
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
    response = client.get(reverse('authorized_item_item', kwargs={"_id": 1}),
                          data={'apikey': apikey.token},
                          content_type='application/json')
    expected_response_content = {
        "id": 1,
        "user_id": user.id,
        "name": "my name is 0"}
    expect(json.loads(response.content)).to.equal(expected_response_content)
    expect(response.status_code).to.equal(200)


def test_get_item_filter_by_user_with_access():
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
    response = client.get(reverse('by_user_authorized_item_item',
                                  kwargs={"_id": 1}),
                          data={'apikey': apikey.token},
                          content_type='application/json')
    expected_response_content = {
        "id": 1,
        "user_id": user.id,
        "name": "my name is 0"}

    expect(json.loads(response.content)).to.equal(expected_response_content)
    expect(response.status_code).to.equal(200)


def test_get_item_filter_by_user_without_access():
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
    response = client.get(reverse('by_user_authorized_item_item',
                                  kwargs={"_id": 2}),
                          data={'apikey': apikey.token},
                          content_type='application/json')
    expected_response_content = {
        "error": "You do not have access to this data"}
    expect(json.loads(response.content)).to.equal(expected_response_content)
    expect(response.status_code).to.equal(400)


def test_get_item_with_non_GET_method():
    response = client.post(reverse('item_item', kwargs={"_id": 1}),
                          content_type='application/json')
    expect(response.status_code).to.equal(403)

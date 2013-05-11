import json
from sure import expect

from django.core.urlresolvers import reverse
from django.test.client import Client

from app.models import Item

client = Client()


def test_search():
    Item.objects.all().delete()
    # item with text containing orange and popularity > 9
    Item.objects.create(
        text="Orange smoothie",
        status=100)

    # item with text containing orange and popularity > 9
    Item.objects.create(
        text="orange juice",
        status=25)

    # item with text not containing orange
    Item.objects.create(
        text="Banana milkshake",
        status=99)

    # item with popularity < 9
    Item.objects.create(
        text="Orange orangutang",
        status=2)

    # only the first two items should be returned
    # by the following search with
    # ?popular=1&contains=orange
    # as the querystring
    response = client.get(reverse('searchable_item_search'),
                          data={"popular": 1, "contains": "orange"},
                          content_type='application/json')

    expected_response_content = {
        "items": [
            {
                "id": 1,
                "text": "Orange smoothie",
                "popularity": 100,
            },
            {
                "id": 2,
                "text": "orange juice",
                "popularity": 25,
             }]}
    expect(json.loads(response.content)).to.equal(expected_response_content)
    expect(response.status_code).to.equal(200)

# Django-EasyRest

## What is EasyRest?
EasyRest is a lightweight framework (less than 160 lines of code!) that allows you to really quickly and flexibly create a READ-ONLY REST API for your models.

## Why would I want to use EasyRest?
* You need a simple read-only REST API for your Backbone/similar app
* You need a read-only API for others to consume. Did you know EasyRest has a simple and extensible authentication system?

## What about those other frameworks?
In exchange for full-featuredness, those other frameworks are hard to setup and use.
EasyRest is really simple to use and even simpler to extend.

## What features do I get with EasyRest?
EasyRest is meant to be simple and cover the most common use cases. So it supports,
* pagination
* authentication
* restricting by requesting user
* search

## How do I install it?
```
pip install django-easyrest
```

## How do I use it?
```
# api.py

from easyrest import API
from .models import Item

api = API()

class ItemResource(APIResource):
    model = Item
    name = 'item'

    def serialize(self, item):
        return {
            'id': item.id,
            'text': item.text,
            'popularity': item.popularity,
        }

api.register(ItemResource)

# urls.py
from django.conf.urls import url, patterns, include
from .api import api

urlpatterns = patterns('', url(r'^api/', include(api.get_urls())))
```
## Declaring a Resource
You only need to specify 3 things when subclassing APIResource:

1. `model`: the Django model you're exposing through the API
2. `name`: this is the name of resource in the url: '/api/{{ name }}/'. If you don't set it, it will fallback to the Model.meta.db_table
3. `serialize` method: returns a serialized version of an instance of your Model, however you want it to. You can reference properties and whatever else. You're not just limited to the model fields.

## Format of Requests and Responses
Let's use the example of ItemResource above.
The urls generated are:
    * /api/item/ - This returns a list of Items
    * /api/item/{int: id}/ - This returns a single serialized Item with the specified id

### GET to the Item list endpoint
```
GET /api/item/ 200

{
   "items": [
       {
           "id": 1,
           "name": "Louis CK"
           "text": "I'm a hilarious comedian",
           "popularity": 99,
       },
       {
           "id": 2,
           "name": "Joffrey Lannister",
           "text": "I'm troubled.",
           "popularity": 2,
       }
    ]
}
```

### GET to the Item single-item endpoint
```
GET /api/item/1/ 200

{
    "id": 1,
    "name": "Louis CK"
    "text": "I'm a hilarious comedian",
    "popularity": 99,
}
```

### GET to the Item single-item endpoint for a nonexistent item
```
GET /api/item/9998/ 400

{
    "error": "No result found matching id: 9998"
}
```

## Pagination
If you want to paginate the results, you just need to set `results_per_page`. Here's an example:

```python
class PaginatedItemResource(APIResource):
    model = Item
    name = 'paginated_item'
    results_per_page = 20

    def serialize(self, item):
        return {
            'id': item.id,
            'text': item.text,
            'popularity': item.popularity,
        }
```
If you don't set `results_per_page`, all of the items will be returned at once.

### How do I request a paginated resource?
Simple.
```
GET /api/item/?page=2
```


## Search
## Authentication
## Restricting by User
## Roadmap

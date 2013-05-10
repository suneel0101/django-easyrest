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

## Registering your resource to the api

    * Create an instance of `easyrest.API`
    * Then register your resource: `api.register(MyResource)`
    * Then include `api.get_urls` in your urlconf

Note that because you are registering resources with an instance of `easyrest.API`, you can conceivably have many different API instances with different resources. EasyRest is flexible in how you use it.

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
EasyRest Authentication is really easy to use and extend, as you'll see below.

### 1. Define an authorization scheme
Decide whether you want your API consumer to pass in an API key through the request GET parameters or the headers or whatever else.

### 2. Set `needs_authentication = True` in your resource declaration

### 3. Define an `authorize` method for your resource
Often you may want the same authorization method for many of your resources.
In that case, you should subclass APIResource and define the `authorize` method, let's call it AuthorizedAPIResource.

Then, all of your model resources can subclass AuthorizedAPIResource.

### Here's an example:

```python
from resteasy.resources import APIResource
from resteasy.auth import get_user_from_GET_param

class AuthorizedAPIResource(APIResource):
    """
    I subclass APIResource and implement the authorize method.
    Many of my resources will require this authorization, so they
    will inherit from this class.
    """
    def authorize(self, request):
        """
        I find the user based on the value of `apikey`
        being passed in as a GET parameter.
        """
        return get_user_from_GET_param(request, "apikey")


class AuthorizedItemResource(AuthorizedAPIResource):
    model = UserItem
    name = 'authorized_item'
    needs_authentication = True

    def serialize(self, item):
        return {
            'name': item.name,
            'id': item.id,
            'user_id': item.user.id,
        }
```

### Authorization helper methods
In easyrest.auth, there are three really useful helper methods:

    * `get_user_from_GET_param(request, param_name)`: extracts API key from the request GET parameter `param_name` and returns the user who owns that API key.
    * `get_user_from_from_request_header`: does the same but from the request header
    * `get_user_from_request`: returns `request.user` if the user is authenticated

These are by no means exhaustive, but they do cover a lot of the ways in which you'll want you're API consumers to authenticate.

If you want to use your own way of authenticating, just write your own `authorize` method, and you're good.

### What happens if an unauthorized person tries to access a protected resource?
If someone tries to access a resource without authorization, they will get a 403 Forbidden response.

## Restricting by User
## Roadmap

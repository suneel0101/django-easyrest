[![Build Status](https://travis-ci.org/suneel0101/django-easyrest.png)](https://travis-ci.org/suneel0101/django-easyrest)

# Django-EasyRest
EasyRest is an ultra-lightweight (160 LOC) read-only REST api framework for Django.

# Table of Contents

* [Installation](#installation)
* [Example](#example)
* [Features](#features)
* [When should I use EasyRest?](#when-should-i-use-easyrest)
* [Usage](#usage)
  * [Declare a Resource](#declare-a-resource)
  * [Define get_queryset](#define-get-queryset)
  * [Search](#search)
  * [Register the Resource with the API](#register-the-resource-with-the-api)
  * [URL Endpoints](#url-endpoints)
  * [Format of Requests and Responses](#format-of-requests-and-responses)
  * [Pagination](#pagination)
  * [Authorization](#authorization)
  * [Builtin APIKey Authorization System](#builtin-apikey-authorization-system)
  * [Authorization Helpers](#authorization-helpers)
  * [Restrict Results by User](#restrict-results-by-user)
* [Bend EasyRest to Your Will](#bend-easyrest-to-your-will)
* [How to Hack on EasyRest](#how-to-hack-on-easyrest)
* [Roadmap](#roadmap)
* [License](#license)

# Installation<a name="installation">&nbsp;</a>
```
pip install django-easyrest
```

# Example<a name="example">&nbsp;</a>
```python
# api.py

from easyrest import API, APIResource
from .models import Item

api = API()

class ItemResource(APIResource):
    model = Item  # the model class you want to expose via the API
    name = 'item'  # name of resource in the url: '/api/{{ name }}/'.

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

# Features<a name="features">&nbsp;</a>
EasyRest is meant to be simple and cover the most common use cases. So it supports,
* search
* pagination
* authentication
* restricting by owner


# When should I use EasyRest?<a name="when-should-i-use-easyrest">&nbsp;</a>
* When you need a simple read-only REST API for your own Backbone/Ember/Angular app
* When you need a read-only API for others to consume - EasyRest has a simple and extensible authorization system.
* Whenever you want!

# Usage<a name="usage">&nbsp;</a>
## Declare a Resource<a name="declare-a-resource">&nbsp;</a>
You only need to specify 3 things when subclassing APIResource:

1. `model`: the Django model you're exposing through the API
2. `name`: this is the name of resource in the url: '/api/{{ name }}/'. If you don't set it, it will fallback to the Model.meta.db_table
3. `serialize` method: returns a serialized version of an instance of your Model, however you want it to. You can reference properties and whatever else. You're not just limited to the model fields.

## Define `get_queryset`<a name="define-get-queryset">&nbsp;</a>
`get_queryset` returns the base results for the resource. It defaults to the following:

```python
def get_queryset(self, get_params):
    # get_params is request.GET.dict()
    return self.model.objects.all()
```

Modify it however you like.

So if you wanted to have the queryset ordered by `id` descending and `status > 7`, you would add to the above `ItemResource` the following method:

```python
    def get_queryset(self):
        return Item.objects.filter(status__gt=7).order_by('-id')
```

## Search: use `get_queryset`<a name="search">&nbsp;</a>


Sometimes you might want to allow your API user to search for a result set rather than just listing the results in a certain order.

The way to set this up in EasyRest is intentionally very barebones so you can extend it and implement the search you want for your resource, no matter how simple or complicated.

#### All you have to do is modify the `get_queryset` method
```python
    def get_queryset(self, get_params):
        """
        Some custom search logic.
        You always have access to the request.GET params
        through `get_params`
        """
        base_queryset = self.model.objects.all()
        filter_kwargs = {}
        if get_params.get("popular"):
            filter_kwargs["status__gte"] = 9

        if get_params.get("contains"):
            filter_kwargs["text__icontains"] = get_params["contains"]
        return base_queryset.filter(**filter_kwargs)
```

The important thing here is you can plug in whatever search system you want. You're not even tied to SQL or the Django ORM. You can use ElasticSearch or whatever backend makes sense for your use case.

#### What is the URL endpoint for a search request?
The URL endpoint for the search request is the same as in list resource request. So if in your root urlconf, you register the api to "/api" and your resource name is "book", you would make the request to `/api/book/`


See [Format of Requests and Responses](#format-of-requests-and-responses)

#### What does a search request to the API look like?
The format of the request will depend on how you implement the `get_queryset` method, but in this case, it looks like this:

`GET /api/searchable_item/?popular=1&contains=fun`


## Register the Resource with the API<a name="register-the-resource-with-the-api">&nbsp;</a>

* Create an instance of `easyrest.API`
* Then register your resource: `api.register(MyResource)`
* Then include `api.get_urls` in your urlconf

Note that because you are registering resources with an instance of `easyrest.API`, you can conceivably have many different API instances with different resources. EasyRest is flexible in how you use it.

## URL Endpoints<a name="url-endpoints">&nbsp;</a>


For each resource you register, there are two URL endpoints: the list endpoint and the item endpoint.
The list endpoint returns a list of instances.
The item endpoint returns a single instance.


Let's use the example of ItemResource above.
We named the resource "item" and included the api urls behind the prefix "/api".
So, the urls generated are:


* `/api/item/` - This returns a list of Items
* `/api/item/{int: id}/` - This returns a single serialized Item with the specified id


## Format of Requests and Responses<a name="format-of-requests-and-responses">&nbsp;</a>

#### GET to the Item list endpoint
```python
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

#### GET to the Item single-item endpoint
```python
GET /api/item/1/ 200

{
    "id": 1,
    "name": "Louis CK"
    "text": "I'm a hilarious comedian",
    "popularity": 99,
}
```

#### GET to the Item single-item endpoint for a nonexistent item
```python
GET /api/item/9998/ 400

{
    "error": "No result found matching id: 9998"
}
```

## Pagination<a name="pagination">&nbsp;</a>
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

#### How do I request a paginated resource?
Simple.
```
GET /api/paginated_item/?page=2
```

## Authorization<a name="authorization">&nbsp;</a>
EasyRest authorization is really easy to use and extend, as you'll see below.

#### 1. Define an authorization scheme
Decide whether you want your API consumer to pass in an API key through the request GET parameters or the headers or whatever else.

#### 2. Set `needs_authorization = True` in your resource declaration

#### 3. Define an `authorize` method for your resource
Here's an example:

```python
from resteasy import APIResource
from resteasy.auth import get_user_from_GET_param

class AuthorizedItemResource(APIResource):
    model = UserItem
    name = 'authorized_item'
    needs_authorization = True

    def serialize(self, item):
        return {
            'name': item.name,
            'id': item.id,
            'user_id': item.user.id,
        }

    def authorize(self, request):
        """
        I find the user based on the value of `apikey`
        being passed in as a GET parameter.
        """
        return get_user_from_GET_param(request, "apikey")
```
#### Advice on many resources sharing same authorization scheme
Often you may want the same authorization method for many of your resources.
In that case, you should subclass APIResource.

Let's call the new class AuthorizedAPIResource.
Define the `authorize` method of AuthorizedAPIResource and then have your model resources inherit from AuthorizedAPIResource

#### What does an example request with authorization look like?
This will depend on authorization scheme, but in the above case where we pass in the apikey in the get request, it would look like this:
```python
GET /api/authorized_item/?apikey=kjhsdf3
```

## Builtin APIKey Authorization System<a name="builtin-apikey-authorization-system">&nbsp;</a>


For your convenience, in `easyrest.models`, there is a simple APIKey model linked to a User.
The `easyrest.auth` methods use this model. 


Creating APIKeys for your consumers is very straightforward. For example,

```python
from easyrest.models import APIKey
from django.contrib.auth.models import User

user = User.objects.create(username='tester', password='123')
new_api_key = APIKey.objects.create(user=user)
```

## Authorization helpers<a name="authorization-helpers">&nbsp;</a>
In easyrest.auth, there are three really useful helper methods:

1. `get_user_from_GET_param(request, param_name)`: extracts API key from the request GET parameter `param_name` and returns the user who owns that API key.
2. `get_user_from_request_header`: does the same but from the request header
3. `get_user_from_request`: returns `request.user` if the user is authenticated

These are by no means exhaustive, but they do cover a lot of the ways in which you'll want you're API consumers to authenticate.

If you want to use your own way of authenticating, just write your own `authorize` method, and you're good.

#### What happens if an unauthorized person tries to access a protected resource?
If someone tries to access a resource without authorization, they will get a 403 Forbidden response.

## Restrict Results by User<a name="restrict-results-by-user">&nbsp;</a>
A lot of the time, we want our API consumers to only access the results that they own.

Imagine an API you can use to get all your Bank Transactions. You want some way of limiting the API user to only retrieving their own bank transactions, so they don't have access to everyone's bank transactions.

To achieve this, you just need to do 1 thing in addition to setting up Authorization as above.
#### Set `user_field_to_restrict_by`

When you declare your resource, you should set `user_field_to_restrict_by` equal to the User field that owns the resource.
This field the same path you would use through the Django Queryset API.

Here are two examples, one simple and one a bit more complicated.

If your UserItem is linked to a User through the field "user",
```python
class UserItem(models.Model):
    name = models.CharField(max_length=250)
    boss = models.ForeignKey('auth.User')
    is_active = models.BooleanField(default=False)
```
You should set `user_field_to_restrict_by="boss"` as follows:
```python
class AuthorizedItemResourceByUser(MyAuthorizedResource):
    model = UserItem
    name = 'restrict_user_authorized_item'
    needs_authorization = True
    user_field_to_restrict_by = 'boss'

    def serialize(self, item):
        return {
            'name': item.name,
            'id': item.id,
            'user_id': item.user.id,
        }
```

#### A more complicated example

```python
class Profile(models.Model):
    owner = models.ForeignKeyField('auth.User')

class UserItem(models.Model):
    name = models.CharField(max_length=250)
    profile = models.ForeignKeyField(Profile)
    is_active = models.BooleanField(default=False)
```

You should set `user_field_to_restrict_by="profile__user"` as follows:
```python
class AuthorizedItemResourceByUser(MyAuthorizedResource):
    model = UserItem
    name = 'restrict_user_authorized_item'
    needs_authorization = True
    user_field_to_restrict_by = 'profile__user'

    def serialize(self, item):
        return {
            'name': item.name,
            'id': item.id,
            'user_id': item.user.id,
        }
```

Now when someone makes an authorized request, the results will be limited to the results that they own.


# Bend EasyRest to Your Will<a name="bend-easyrest-to-your-will">&nbsp;</a>
Here are some facts.

* EasyRest is 160 lines of code.
* You may have custom needs for your API.
* If you read the source code, you'll know how to extend EasyRest to suit your needs.

#### My Recommendations
Whether you want to change the url schema, add more CRUD methods, or change the way data is retrieved,
always feel free to subclass `easyrest.API`, `easyrest.APIResource`, and the `ListView` and `ItemView` to your heart's desire.

Let me know how you extend EasyRest, I'd be excited to learn and potentially get some pull requests!

# How to Hack on EasyRest<a name="how-to-hack-on-easyrest">&nbsp;</a>
1. git clone this repo
2. create a virtualenv and install the requirements via `pip install -r requirements.txt`
3. under /tests, run `python manage.py syncdb`
4. to run the tests, in the root directory run `make test`

Happy hacking!


# Roadmap<a name="roadmap">&nbsp;</a>

* I'm thinking about whether to support the other CRUD operations.
* Javascript Framework template tags so that when setting up Backbone sync for example, all you have to do is something like {% backbone mymodel %}{% endbackbone %} and your endpoints are already set up.

If you have any suggestions, please let me know.


# License<a name="license">&nbsp;</a>

(The MIT license)

Copyright (c) 2013 Suneel Chakravorty <suneel0101@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

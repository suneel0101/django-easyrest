# Django-EasyRest
EasyRest is a lightweight framework (less than 160 lines of code!) that allows you to really quickly and flexibly create a READ-ONLY REST API for your models.

## Table of Contents

* [Installation](#installation)
* [Example](#example)
* [When should I use EasyRest?](#when-should-i-use-easyrest)
* [Features](#features)
* [Usage](#usage)
  * [Declare a Resource](#declare-a-resource)
  * [Register the Resource with the API](#register-the-resource-with-the-api)
  * [Format of Requests and Responses](#format-of-requests-and-responses)
  * [Enable Pagination](#enable-pagination)
  * [Enable Search](#enable-search)
  * [Use Authentication](#use-authentication)
  * [Authorization Helpers](#authorization-helpers)
  * [Restrict Results by User](#restrict-results-by-user)
* [How to Customize EasyRest](#how-to-customize-easyrest)
* [How to Hack on EasyRest](#how-to-hack-on-easyrest)
* [Roadmap](#roadmap)
* [License](#license)

## Installation<a name="installation">&nbsp;</a>
```
pip install django-easyrest
```

## Example<a name="example">&nbsp;</a>
```python
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

## When should I use EasyRest?<a name="when-should-i-use-easyrest">&nbsp;</a>
* When you need a simple read-only REST API for your Backbone/similar app
* When ou need a read-only API for others to consume. Did you know EasyRest has a simple and extensible authentication system?
* Whenever you want!

## Features<a name="features">&nbsp;</a>
EasyRest is meant to be simple and cover the most common use cases. So it supports,
* pagination
* authentication
* restricting by owner
* search

# Usage<a name="usage">&nbsp;</a>
## Declare a Resource<a name="declare-a-resource">&nbsp;</a>
You only need to specify 3 things when subclassing APIResource:

1. `model`: the Django model you're exposing through the API
2. `name`: this is the name of resource in the url: '/api/{{ name }}/'. If you don't set it, it will fallback to the Model.meta.db_table
3. `serialize` method: returns a serialized version of an instance of your Model, however you want it to. You can reference properties and whatever else. You're not just limited to the model fields.

You can also specify the `get_queryset` method, which will return the base queryset that will be used in the item-list endpoint as well as the search endpoint.
So if you wanted to have the queryset ordered by `id` descending and `status > 7`, you would add to the above `ItemResource` the following method:

```python
    def get_queryset(self):
        return Item.objects.filter(status__gt=7).order_by('-id')
```

Use this method to customize the set of results you want returned any way you like.
For example, you can do preprocessing as we did above with the `status` as well as specify an ordering.

## Register the Resource with the API<a name="register-the-resource-with-the-api">&nbsp;</a>

* Create an instance of `easyrest.API`
* Then register your resource: `api.register(MyResource)`
* Then include `api.get_urls` in your urlconf

Note that because you are registering resources with an instance of `easyrest.API`, you can conceivably have many different API instances with different resources. EasyRest is flexible in how you use it.

## Format of Requests and Responses<a name="format-of-requests-and-responses">&nbsp;</a>
Let's use the example of ItemResource above.
The urls generated are:
    * /api/item/ - This returns a list of Items
    * /api/item/{int: id}/ - This returns a single serialized Item with the specified id

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

## Enable Pagination<a name="enable-pagination">&nbsp;</a>
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
GET /api/item/?page=2
```


## Enable Search<a name="enable-search">&nbsp;</a>

Sometimes you might want to allow your API user to search for a result set rather than just listing the results in a certain order.
The way to set this up in EasyRest is intentionally very barebones so you can extend it and implement the search you want for your resource, no matter how simple or complicated.

#### All you have to do is define the `search` method
```python
class SearchableItemResource(APIResource):
    model = Item
    name = 'searchable_item'
    results_per_page = 20

    def serialize(self, item):
        return {
            'id': item.id,
            'text': item.text,
            'popularity': item.popularity,
        }

    def search(self, get_params):
        """
        Some custom search logic.
        You always have access to the request.GET params
        through `get_params`
        """
        filter_kwargs = {}
        if get_params.get("popular"):
            filter_kwargs["popularity__gte"] = 9
         
        if get_params.get("contains"):
            filter_kwargs["text__icontains"] = get_params["contains"]
        return self.get_queryset().filter(**filter_kwargs)
```

The important thing here is you can plug in whatever search system you want. You're not even tied to SQL or the Django ORM. You can use ElasticSearch or whatever backend makes sense for your use case. You just have to define the `search` method that takes a dictionary of request GET params.

#### Make a search request
The URL will be "/{resource name}/search/"
The format of the request will depend on how you implement the `search` method, but in this case, it looks like this:

`GET /api/searchable_item/search/?popular=1&contains=fun`

## Use Authentication<a name="use-authentication">&nbsp;</a>
EasyRest Authentication is really easy to use and extend, as you'll see below.

#### 1. Define an authorization scheme
Decide whether you want your API consumer to pass in an API key through the request GET parameters or the headers or whatever else.

#### 2. Set `needs_authentication = True` in your resource declaration

#### 3. Define an `authorize` method for your resource
Here's an example:

```python
from resteasy.resources import APIResource
from resteasy.auth import get_user_from_GET_param

class AuthorizedItemResource(APIResource):
    model = UserItem
    name = 'authorized_item'
    needs_authentication = True

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

#### What does an example authenticated request look like?
This will depend on authorization scheme, but in the above case where we pass in the apikey in the get request, it would look like this:
```python
GET /api/authorized_item/?apikey=kjhsdf3
```

## Authorization helpers<a name="authorization-helpers">&nbsp;</a>
In easyrest.auth, there are three really useful helper methods:

1. `get_user_from_GET_param(request, param_name)`: extracts API key from the request GET parameter `param_name` and returns the user who owns that API key.
2. `get_user_from_from_request_header`: does the same but from the request header
3. `get_user_from_request`: returns `request.user` if the user is authenticated

These are by no means exhaustive, but they do cover a lot of the ways in which you'll want you're API consumers to authenticate.

If you want to use your own way of authenticating, just write your own `authorize` method, and you're good.

#### What happens if an unauthorized person tries to access a protected resource?
If someone tries to access a resource without authorization, they will get a 403 Forbidden response.

## Restrict Results by User<a name="#restrict-results-by-user">&nbsp;</a>
A lot of the time, we want our API consumers to only access the results that they own.

Imagine an API you can use to get all your Bank Transactions. You want some way of limiting the API user to only retrieving their own bank transactions, so they don't have access to everyone's bank transactions.

To achieve this, you just need to do 1 thing in addition to setting up Authentication as above.
#### Set `restrict_by_user`
When you declare your resource, you should set `restrict_by_user` equal to the field path to the User field corresponding to the owner, the same path you would use through the Django Queryset API.

If your UserItem is linked to a User through the field "user", for example:
```python
class UserItem(models.Model):
    name = models.CharField(max_length=250)
    user = models.ForeignKey('auth.User')
    is_active = models.BooleanField(default=False)
```
You should set `restrict_by_user="user"` as follows:
```python
class AuthorizedItemResourceByUser(MyAuthenticatedResource):
    model = UserItem
    name = 'restrict_user_authorized_item'
    needs_authentication = True
    restrict_by_user = 'user'

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

You should set `restrict_by_user="profile__user"` as follows:
```python
class AuthorizedItemResourceByUser(MyAuthenticatedResource):
    model = UserItem
    name = 'restrict_user_authorized_item'
    needs_authentication = True
    restrict_by_user = 'profile__user'

    def serialize(self, item):
        return {
            'name': item.name,
            'id': item.id,
            'user_id': item.user.id,
        }
```

## How to Customize EasyRest<a name="how-to-customize-easyrest">&nbsp;</a>
You may have custom needs for your api. Here's some advice on how to extend EasyRest to meet those needs.

* If you want to modify what the URLs look like, you should subclass `easyrest.API` and use that subclass as your API.
* If you want to modify how results are retrieved, subclass `APIResource` and modify the `get_list` and `get_one` methods
* If you want to add POST, CREATE or UPDATE funcionality, subclass the views and use those views in your `get_urls` method (to do that would have to subclass API, as mentioned above). In addition, you'll probably want to add methods to `APIResource` to deal with those CRUD operations.
* If you want to plug in a different authentication/authorization scheme, define the `authorize` method of the APIResource.

These are just a few guidelines. If you modify it in other cool ways, please let me know, I'd be excited to learn!

The *main point* is that since there are only 160 lines of code, you can see the inner workings of this library really easily and feel free to bend it to your will!

## How to Hack on EasyRest<a name="how-to-hack-on-easyrest">&nbsp;</a>
1. git clone this repo
2. create a virtualenv and install the requirements via `pip install -r requirements.txt`
3. under /tests, run `python manage.py syncdb`
4. to run the tests, in the root directory run `make test`

Happy hacking!


## Roadmap<a name="roadmap">&nbsp;</a>
I'm thinking about whether to support the other CRUD operations.
If you have any suggestions, please let me know.


## License<a name="license">&nbsp;</a>

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

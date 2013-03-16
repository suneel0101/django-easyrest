# Django-Restroom: a super lightweight REST API framework

### Status: This project is still under development!

Whether you want to create an API for your product for external consumption or you just want to expose a REST API for your own frontend application, Django-Restroom is an incredibly easy and fast way to accomplish that.
You just register your models and include the restroom urls.

There are also additional features such as authentication, pagination and the ability to restrict a resource to return results owned by the requesting user.

## 1. Register your models
Basic Usage:
```python
from myapp.models import MyModel
from restroom.core import API
api = API()
api.register(MyModel)
```
This enables GET requests to the RESTful endpoints for the resource `MyModel`.
GET requests will return serialized results with all of the fields of the model.

However, `register` does take an options dictionary with the following parameters:

### `http_methods`
These are the HTTP methods of requests you want to enable for that model resource.
You can pass in any sublist of ["GET", "POST", "DELETE", "PUT"]
If you do not pass in anything, it will default to only allowing GET requests.

Sample Usage:
```python
from myapp.models import MyModel
from restroom.core import API
api = API()
api.register(MyModel, {"http_methods": ["GET", "POST", "PUT"]})
```

Any `DELETE` requests to the RESTful endpoints for `MyModel` will return an empty 403 response forbidden.

### `fields`

These are the fields of the model you want to expose to consumers of your api.
The object's `id` will always be exposed. If you do not pass in anything, it will default to exposing all fields.
When the REST endpoints for a model are requested by any method other than the ones you have allowed, a 403 Forbidden response will be returned.

Sample usage:
```python
from restroom.core import api
from django.db import models

api = API()

class Book(models.Model):
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=100)
    date_published = models.DateTimeField()

api.register(Book, {"fields": ["title", "author"]})
```
The results will be serialized so that only the `id`, `title`, `author` fields are in the return JSON.

There are two additional optional parameters `needs_auth` and `only_for_user` which will be discussed in the Authentication section.

### Recommended pattern of registering your models
It's easiest to the do following, although after using this library just once, you'll feel comfortable enough to register your models however and wherever you'd like.

In the same level as your main urlconf, create a file `api.py`
In `api.py`:
```python
from restroom.core import API
from apps.thisapp.models import X, Y, Z
from apps.otherapp.models import A, B, C
...
api = API()
api.register(X, {"fields": ["text", "slug"]})
api.register(Y, {"http_methods": ["GET", "POST"]})
...
```


## 2. Include urls in your main urlconf
Follow the above recommended pattern models. Then your main urls.py
```python
from .api import api
...
urlpatterns += patterns('', url('r^api/', include(api.get_urls())))
```

## 3. REST endpoints are created automatically
Suppose you have registered the model `EmailRecord` from the app `emailer` with `http_methods=['GET', 'POST', 'DELETE', 'PUT']` and the `fields=['user', 'timestamp', 'body']`.
Then you have included the urls under the prefix `/api/` as above.


Then these are the REST endpoints you can request:

### /api/emailer_emailrecord/
* This is a list resource.
* GET will return a list of results which match the query.
* PUT will modify all results that match the query.
* POST will create a new object.
* DELETE is always forbidden.

### /api/emailer_emailrecord/{int: id}/
* This is an item resource.
* GET will return the object with that id.
* PUT will modify the object.
* DELETE will delete the object.
* POST is always forbidden.

## 4. Format of Requests and Responses

### GET /api/emailer_emailrecord/
Responds with a list of all `EmailRecord` objects, for example:

```
HTTP 200
{
    "items": [
        {"id": 1,
         "body": "Dear sir, will you sign up for my site?",
         "timestamp": "2013-03-15T20:56:13.652681"},
        {"id": 2,
         "body": "Dear miss, will you sign up for my site?",
         "timestamp": "2013-03-16T20:33:19.952455"},
        {"id": 3,
         "body": "Dear friend, will you sign up for my site?",
         "timestamp": "2013-03-18T16:14:21.322591"}
    ]  
}

```


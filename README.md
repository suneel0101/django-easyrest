# Django-Restroom: a super lightweight REST API framework

### Status: This project is still under development!

Whether you want to create an API for your product for external consumption or you just want to expose a REST API for your own frontend application, Django-Restroom is an incredibly easy and fast way to accomplish that.

There are only two steps:

1. Decorate the model classes you want to expose in a RESTful API with `@expose`
2. Include restroom.urls in your main urls.py file, which will create the REST endpoints.


## 1. @expose your Models

`@expose` registers a Django model to your API.

It takes two optional keyword arguments:

### `allowed_methods`

These are the HTTP methods of requests you want to enable for that model resource.
You can pass in any sublist of ["GET", "POST", "DELETE", "PUT"]
If you do not pass in anything, it will default to only allowing GET requests.

### `fields`

These are the fields of the model you want to expose to consumers of your api.
The object's `id` will always be exposed. If you do not pass in anything, it will default to exposing all fields.
When the REST endpoints for a model are requested by any method other than the ones you have allowed, a 403 Forbidden response will be returned.

### Sample usage:
```python
from django.db import models
from restroom import expose

@expose(allowed_methods=["GET", "POST", "DELETE", "PUT"], fields=["title", "author"])
class Book(models.Model):
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=100)
    date_published = models.DateTimeField()

@expose
class Movie(models.Model):
    title = models.CharField(max_length=150)
    popular = models.BooleanField()
```

While `@expose` is the intended interface for registering a model, in case the list of fields is too long, you can always do the following:

```python
from restroom import api

api.register(Book, {
    "allowed_methods": ["GET", "POST", "DELETE", "PUT"],
    "fields": ["title", "author"]})
````


## 2. Create REST endpoints automatically

Once you have exposed the models you want to create a RESTful API for, you should include the following in your `urls.py`:

```python
from django.conf.urls import url, patterns
import restroom

urlpatterns += patterns("",
   url(r"^api/", include(restroom.urls)),
)
```

This will automatically create REST endpoints for each of your registered models.
Let’s use the examples of the Book and Movie models registered above.

### GET /api/book/
This returns a list of Book objects.
Since we exposed only the ‘title’ and the ‘author’, those are the only fields we will see in the response.

#### Sample response
```
GET /api/book/
HTTP 200 OK

{
    "results": [
        {"id": 1, "title": "Crime and Punishment", "author": "Fyodor Dostoevsky"},
        {"id": 2, "title": "Harry Potter and the Sorcerer’s Stone", "author": "JK Rowling"}
    ]
}
```

#### Querying API
To filter the set of results, you can also request this endpoint with a `query` parameter, which is a list of filter parameters.
specifying the field you want to query on, the operation (=, gte, in, etc), and the restricting value. See below for an example.
(This pattern was inspired by Flask Restless, an awesome API framework for Flask)
```
GET /api/book/
{"query": [
    {"field": "id",
     "operator": "in",
     "value": [1, 2]},
     {"field": "title",
     "operator": "=",
     "value": "Crime and Punishment"}
     ]
}

HTTP 200 OK
{
    "results": [
        {"id": 1, "title": "Crime and Punishment", "author": "Fyodor Dostoevsky"}
    ]
}
```

### GET /api/book/{int: id}
This returns the Book with the specified ID.

#### Sample responses
```
GET /api/book/1/
HTTP 200 OK

{"id": 1, "title": "Crime and Punishment", "author": "Fyodor Dostoevsky"}
```

```
GET /api/book/3/
HTTP 200 OK

{"error": "no object found matching id 3"}
```

### DELETE /api/book/{int: id}
This deletes the Book object with the specified ID.

#### Sample responses
```
DELETE /api/book/1/
HTTP 200 OK

{"status": "deletion successful"}
```

```
DELETE /api/book/3/
HTTP 400

{"error": "no object found matching id 3"}
```

Remember for the Movie object, we didn’t pass in any allowed methods, so it defaults to only allowing GET requests. So we see the result of trying to POST to the Movie API endpoint.

```
DELETE /api/movie/1
HTTP 403 Forbidden

No content.
```

### POST /api/book/
This creates a Book with the field values as specified in the request.POST QueryDict.

#### Sample responses

```
POST /api/book/
{"title": "1984", "author": "George Orwell"}

HTTP 200 OK
{"id": 3, "title": "1984", "author": "George Orwell"}
```

If invalid fields or invalid values are passed in, the response will contain an error message.

```
POST /api/book/
{"short_title": "LOTR", "author": "JRR Tolkien", "title": "Lord of the Rings"}

HTTP 400
{"error": "score is an invalid field"}
```

### PUT /api/book/{int: id}
This updates the Book with the specified ID.

#### Sample responses

```
PUT /api/book/1/
{"title": "The Brothers Karamazov"}

HTTP 200 OK
{"id": 1, "title": "The Brothers Karamazov", "author": "Fyodor Dostoevsky"}
```

```
PUT /api/book/5/
{"title": "Nonexistent Book"}

HTTP 400
{"error": "no object found matching id 5"}
```

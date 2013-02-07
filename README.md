# Django-Restroom

Django-Restroom is a lightweight API framework for Django.

All you have to do is decorate the model classes that you want to expose in a RESTful API and include `restroom.urls` in your main urls.py file and you've got yourself an API for your app.

## Usage:

In  `myapp/models.py`:

```python
from django.db import models
from restroom import expose

@expose(allowed_methods=["GET", "POST"], fields=["id", "title", "author"])
class Book(models.Model):
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=100)
    status = models.IntegerField(default=7)
    is_active = models.BooleanField(default=True)
    date_published = models.DateTimeField(auto_now_add=True)
```

In your `urls.py`:

```python
import restroom

urlpatterns = ("",
   ...
   url(r"^whateveryouwant/", include(restroom.urls)),
   ...
)
```

In the shell:

```
>>> from myapp.models import Book
>>> Book.objects.create(title="Best book ever", author="Yours truly")
```

## Accessing the REST endpoints:
`GET /whateveryouwant/myapp_book/` responds with
```
[{"id": 1, "title": "Best book ever", "author": "Yours truly"}]
```
`GET /whateveryouwant/myapp_book/1/` responds with
```
{"id": 1, "title": "Best book ever", "author": "Yours truly"}
```
`POST /whateveryouwant/myapp_book/?title=Awesomeness&author=Zeus` responds with
```
{"id": 2, "title": "Awesomess", "author": "Zeus"}
```
This endpoint creates a record and returns it serialized.

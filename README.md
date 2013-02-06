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
    status = models.IntegerField()
    is_active = models.BooleanField()
    date_published = models.DateTimeField()
    publisher = models.ForeignKey('otherapp.Publisher')
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

Finally, when a GET request is made to `/whateveryouwant/myapp_book/`, here's the response:
```
{"results": [{"id": 1, "title": "Best book ever", "author": "Yours truly"}]}
```

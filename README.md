# Django-Restroom

Django-Restroom is a lightweight API framework for Django.

All you have to do is decorate the model classes that you want to expose in a RESTful API and include `restroom.urls` in your main urls.py file and you've got yourself an API for your app.

## Sample usage:

In  `myapp/models.py`:

```python
from django.db import models
from restroom import expose

@expose(methods"GET", "POST"], fields=["id", "title", "author"])
class Book(models.Model):
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=100)
```

In your `urls.py`:

```python
urlpatterns = ("",
   …
   url(r"^whateveryouwant/", include(restroom.urls)),
   …
)
```

In the shell:

```
>>> from myapp.models import Book
>>> Book.objects.create(title="Best book ever", author="Yours truly")
```

Finally, when a GET request is made `/whateveryouwant/myapp_book/`, here's the response:
```
[{"title": "Best book ever", "author": "Yours truly"}]
```

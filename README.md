# Django-EasyRest: a lightweight readonly REST API framework

# What is EasyRest?
EasyRest is a small library (less than 160 lines of code!) that allows you to really quickly and flexibly create a READ-ONLY REST API for your models.

# Why would I want to use EasyRest?
If you're building a front-end heavy website that uses Backbone or similar:
    * All you need in the backend is a REST API to read from.
    * With EasyRest makes this ridiculously simple.

If you need a simple and extensible read-only API for your existing product:
    * you do the same thing.
    * EasyRest has a really simple built-in authentication system so you can give out API keys to your API consumers and you're all ready to go.
    * You can also plug in your custom API authentication system easily

# What's the advantage of using EasyRest over Django-Rest, Tastypie, etc?
In exchange for full-featuredness, those other frameworks are hard to setup and use.
EasyRest is really simple to use and even simpler to extend.

# What features do I get with EasyRest?
EasyRest is meant to be a straightforward read-only api for the most common use cases. So it supports,
* pagination
* authentication
* restricting by requesting user
* search

# How do I install it?
```pip install django-easyrest```

# How do I use it?
## Basic Usage
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
from app.api import api

urlpatterns = patterns('', url(r'^test/', include(api.get_urls())))
```
## Declaring a Resource
## Pagination
## Authentication
## Search
## Format of Requests and Responses
## Roadmap

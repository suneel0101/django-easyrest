# Django-EasyRest

## What is EasyRest?
EasyRest is a lightweight framework (less than 160 lines of code!) that allows you to really quickly and flexibly create a READ-ONLY REST API for your models.

## Why would I want to use EasyRest?
* You need a simple read-only REST API for your Backbone/similar app
* You need a read-only API for others to consume. Did you know EasyRest has a simple and extensible authentication system?

## What's the advantage of using EasyRest over Django-Rest, Tastypie, etc?
In exchange for full-featuredness, those other frameworks are hard to setup and use.
EasyRest is really simple to use and even simpler to extend.

## What features do I get with EasyRest?
EasyRest is meant to be simple and cover the most common use cases. So it supports,
* pagination
* authentication
* restricting by requesting user
* search

## How do I install it?
```pip install django-easyrest```

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
from app.api import api

urlpatterns = patterns('', url(r'^test/', include(api.get_urls())))
```
## Declaring a Resource
## Pagination
## Authentication
## Search
## Format of Requests and Responses
## Roadmap

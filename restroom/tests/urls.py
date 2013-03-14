from django.conf.urls import patterns, include, url
from .api import api


urlpatterns = patterns('',
                       url(r'^awesome_api/', include(api.get_urls())),)

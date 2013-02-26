from restroom import api

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^api/', include(api.get_urls())),
)

from django.conf.urls import url, patterns, include
from app.api import api

urlpatterns = patterns('', url(r'^test/', include(api.get_urls())))

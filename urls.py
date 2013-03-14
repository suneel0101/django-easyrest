from django.conf.urls import url, patterns, include

urlpatterns = patterns('', url(r'^test/', include('restroom.tests.urls')))

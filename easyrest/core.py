from django.conf.urls import url, patterns
from .views import ItemView, ListView, SearchView


class API(object):
    def __init__(self):
        self.resources = []

    def register(self, resource):
        self.resources.append(resource())

    def get_urls(self):
        urls = []
        for resource in self.resources:
            if hasattr(resource, 'search'):
                urls.append(url(r"^{}/search/$".format(resource.name),
                                SearchView.as_view(resource=resource),
                                name="{}_search".format(resource.name)))
            urls.extend([
                url(r"^{}/$".format(resource.name),
                    ListView.as_view(resource=resource),
                    name="{}_list".format(resource.name)),
                url(r"^{}/(?P<_id>[\d]+)/$".format(resource.name),
                    ItemView.as_view(resource=resource),
                    name="{}_item".format(resource.name)),
            ])
        return patterns('', *urls)

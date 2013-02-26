from sure import expect

from restroom.urls import urlpatterns
from restroom import api

from tests.unit.test_api import transform_to_attrs_dict


def test_restroom_urls_equals_api_url_patterns():
    (expect(transform_to_attrs_dict(urlpatterns))
     .to.equal(transform_to_attrs_dict(api.get_urls())))

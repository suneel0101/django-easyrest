from sure import expect
from mock import patch, Mock
from django.conf.urls import patterns, url
from restroom.api import API
from restroom.tests.models import Modelo


def assert_patterns_are_equal(pattern_x, pattern_y):
    assert len(pattern_x) == len(pattern_y), (
        "X has {} items while Y has {} items".format(
            len(pattern_x), len(pattern_y)))
    fields = ['_callback_str', 'name', '_regex']
    for i in range(len(pattern_x)):
        if not all(
            [getattr(pattern_x[i], field) == getattr(pattern_y[i], field)
             for field in fields]):
            raise AssertionError("The patterns are not equal")
    return True


@patch('restroom.api.RestroomResource')
def test_register(RestroomResource):
    "API.register should add a RestroomResource-wrapped model to its resources"
    RestroomResource.return_value = "a restroom resource"
    api = API()
    api.register(Modelo)
    expect(api.resources).to.equal(["a restroom resource"])
    RestroomResource.assert_called_once_with(Modelo, {})


@patch('restroom.api.RestroomResource')
def test_register_with_options(RestroomResource):
    "API.register with options"
    RestroomResource.return_value = "a restroom resource"
    api = API()
    api.register(Modelo, {'http_methods': ['GET', 'POST']})
    expect(api.resources).to.equal(["a restroom resource"])
    RestroomResource.assert_called_once_with(Modelo,
                                             {'http_methods': ['GET', 'POST']})


@patch('restroom.api.RestroomItemView')
@patch('restroom.api.RestroomListView')
def test_get_urls(RestroomListView, RestroomItemView):
    "API.get_urls"
    RestroomItemView.as_view.return_value = 'item view'
    RestroomListView.as_view.return_value = 'list view'
    api = API()
    resource_1 = Mock()
    resource_1.name = 'one_resource'
    resource_2 = Mock()
    resource_2.name = 'another_resource'
    api.resources = [resource_1, resource_2]
    urls = [
        url(
            r"^one_resource/$",
            "list view",
            name="one_resource_list"),
        url(
            r"^one_resource/(?P<_id>[\d]+)/$",
            "item view",
            name="one_resource_item"),
        url(
            r"^another_resource/$",
            "list view",
            name="another_resource_list"),
        url(
            r"^another_resource/(?P<_id>[\d]+)/$",
            "item view",
            name="another_resource_item"),
    ]
    assert_patterns_are_equal(api.get_urls(), patterns('', *urls))

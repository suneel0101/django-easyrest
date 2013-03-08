from sure import expect
from mock import patch
from restroom.api import API
from restroom.tests.models import Modelo


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

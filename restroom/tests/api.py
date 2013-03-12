from restroom.core import API
from .models import Modelo


api = API()
api.register(Modelo, {'fields': ['text', 'slug', 'awesome'],
                      'http_methods': ['GET', 'POST', 'PUT', 'DELETE']})

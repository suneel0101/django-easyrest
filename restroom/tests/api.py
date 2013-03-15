from restroom.core import API
from .models import (
    Modelo,
    Modela,
    Modelb,
    Modelc,
    ModelAuthed,
    ModelFK,
    ModelFKID,
    ModelM2M)


api = API()
api.register(Modelo, {'fields': ['text', 'slug', 'awesome'],
                      'http_methods': ['GET', 'POST']})

api.register(Modela, {'fields': ['text', 'slug', 'awesome'],
                      'http_methods': ['POST']})

api.register(Modelb, {'fields': ['text', 'timestamp', 'slug', 'awesome'],
                      'http_methods': ['PUT', "GET"]})

api.register(Modelc, {'fields': ['text', 'slug', 'awesome'],
                      'http_methods': ['DELETE']})

api.register(ModelFK, {'fields': ['text', 'slug', 'awesome', 'foreign']})

api.register(ModelFKID)

api.register(ModelAuthed,
             {'fields': ['text', 'slug', 'awesome'], 'needs_auth': True})

api.register(ModelM2M)

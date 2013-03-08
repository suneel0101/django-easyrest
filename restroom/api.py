from .resources import RestroomResource


class API(object):
    def __init__(self):
        self.resources = []

    def register(self, model, options={}):
        self.resources.append(RestroomResource(model, options))

from .api import API
from .errors import RestroomError

api = API()


def expose(api=api, **options):
    """
    This is the recommended way of exposing a model
    to be accessible via the Restroom's Restful API.

    Example 1:

    # limited to GET requests
    # all fields will be exposed in the data
    @expose()
    class My Model(models.Model):
        pass

    Example 2:

    # limited to GET and POST requests
    # only the id and name will be exposed in the data
    @expose(allowed_methods=['GET', 'POST'], fields=['id', name'])
    class Person(models.Model):
        name = models.CharField(max_length=100)
        is_active = models.BooleanField(default=False)
    """
    def expose_api(kls, api=api):
        api.register(kls, options)
        return kls
    return expose_api

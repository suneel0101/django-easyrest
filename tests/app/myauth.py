from restroom.resources import APIResource
from restroom.auth import get_user_from_GET_param


class MyAuthenticatedResource(APIResource):
    """
    I subclass APIResource to implement the authorize method.
    """
    def authorize(self, request):
        """
        I find the user based on the value of `apikey`
        being passed in as a GET parameter.
        """
        return get_user_from_GET_param(request, "apikey")

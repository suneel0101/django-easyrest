from .models import APIKey


def authorize(request):
    # if request.user.is_authenticated():
    #     return True
    user = None
    token = request.META.get('RESTROOM_API_KEY')
    if token:
        try:
            api_key = APIKey.objects.get(token=token)
        except APIKey.DoesNotExist:
            pass
        else:
            user = api_key.user
    return user

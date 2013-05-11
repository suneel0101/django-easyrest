from .models import APIKey


def get_user_from_request(request):
    if request.user.is_authenticated():
        return request.user


def get_user_from_GET_param(request, param_name):
    token = request.GET.get(param_name)
    try:
        return APIKey.objects.get(token=token).user
    except APIKey.DoesNotExist:
        pass


def get_user_from_request_header(request, param_name):
    token = request.META.get(param_name)
    try:
        return APIKey.objects.get(token=token).user
    except APIKey.DoesNotExist:
        pass

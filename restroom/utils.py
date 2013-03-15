import json
import datetime
from decimal import Decimal
from django.db import models
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


def get_val(obj, name):
    value = getattr(obj, name)
    if (isinstance(value,
                   datetime.datetime) or isinstance(value, datetime.date)):
        value = value.isoformat()
    elif isinstance(value, bool):
        value = int(value)
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, models.Model):
        value = value.pk
    try:
        json.dumps(value)
    except TypeError:
        return "Could not serialize {}".format(str(value))
    return value

import json
import datetime
from decimal import Decimal


def get_val(obj, name):
    value = getattr(obj, name)
    if (isinstance(value,
                   datetime.datetime) or isinstance(value, datetime.date)):
        return value.isoformat()
    elif isinstance(value, bool):
        return int(value)
    elif isinstance(value, Decimal):
        return float(value)
    try:
        json.dumps(value)
    except TypeError:
        return "Could not serialize {}".format(str(value))
    return value

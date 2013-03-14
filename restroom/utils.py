import datetime


def get_val(obj, name):
    value = getattr(obj, name)
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    elif isinstance(value, bool):
        return int(value)
    return value

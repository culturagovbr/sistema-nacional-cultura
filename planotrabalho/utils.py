import re
from datetime import date


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def add_anos(data, anos):
    try:
        return data.replace(year=data.year + anos)
    except ValueError:
        return data + (date(data.year + anos, 1, 1) - date(data.year, 1, 1))

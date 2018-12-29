import datetime
from typing import Optional

import attr
import dpath
import pytz


def dpath_get(glob):
    """
    Getter which returns one value by dpath glob
    """

    def func(obj: dict, field: attr.Attribute):
        try:
            return dpath.get(obj, glob)
        except KeyError:
            return field.default

    return func


def dpath_get_datetime(glob):
    """
    Getter which returns one timestamp value by dpath glob
    """

    def func(obj: dict, field: attr.Attribute):
        try:
            value = dpath.get(obj, glob)
        except KeyError:
            return field.default
        return ts(value)

    return func


def dpath_values(glob):
    """
    Getter which returns a list of values by dpath glob
    """
    return lambda obj, field: dpath.values(obj, glob)


def ts(value: Optional[int]) -> Optional[datetime.datetime]:
    if value:
        dt = datetime.datetime.fromtimestamp(value / 1000)
        return pytz.utc.localize(dt)

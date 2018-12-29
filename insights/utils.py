import datetime
import gzip
import io
import json
from typing import Iterator, Any, MappingView, Union

import attr


def json_records_gz(
        object_list: Union[Iterator[Any], MappingView[Any]]) -> io.BytesIO:
    """
    Turn a list or iterator of objects into a gzipped file with
    newline-separated JSON-encoded records and return a file object.

    This object can be later on stored to a file or uploaded to S3
    """
    fileobj = io.BytesIO()
    fileobj_gz = gzip.GzipFile(fileobj=fileobj, mode='w')
    for obj in object_list:
        line = json_dumps(obj) + '\n'
        fileobj_gz.write(line.encode('utf-8'))
    fileobj_gz.close()
    fileobj.seek(0)
    return fileobj


def json_dumps(obj):
    """
    Convert object to JSON using compact representation and custom json default
    """
    return json.dumps(
        obj, separators=',:', default=json_default, sort_keys=True)


def json_default(obj):
    if attr.has(obj.__class__):
        return attr.asdict(obj)
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%FT%TZ')
    if isinstance(obj, datetime.date):
        return obj.strftime('%F')
    return repr(obj)

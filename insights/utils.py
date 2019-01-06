import datetime
import hashlib
import hmac
import io
import json
import re
from typing import Any, Iterator, MappingView, Optional, Union

import attr
from django.conf import settings
from django.utils.encoding import force_bytes
from google.cloud import bigquery

ObjectList = Union[Iterator[Any], MappingView[Any]]

client = bigquery.Client()


def bigquery_upload(object_list: ObjectList,
                    table_id: str,
                    job_id: Optional[str] = None,
                    async: bool = True):
    """
    Load the list of objects to bigquery table.

    job_id can be set explicitly to exclude processing duplicates

    If async is set to True, the function doesn't wait for the operation to
    complete successfully, and return as soon as data are sent to the server.
    """
    # Create job config
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    job_config.autodetect = True
    job_config.create_disposition = bigquery.CreateDisposition.CREATE_IF_NEEDED
    job_config.schema_update_options = [
        bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
        bigquery.SchemaUpdateOption.ALLOW_FIELD_RELAXATION
    ]
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

    # Create the file object to load
    records_fd = json_records(object_list)

    # Run the query
    dataset_ref = client.dataset(settings.BIGQUERY_DATASET_ID)
    table_ref = dataset_ref.table(table_id)
    job = client.load_table_from_file(
        records_fd, table_ref, job_id=job_id, job_config=job_config)

    if not async:
        job.result()


def json_records(object_list: ObjectList) -> io.BytesIO:
    """
    Turn a list or iterator of objects into a file object with
    newline-separated JSON-encoded records
    """
    fileobj = io.BytesIO()
    for obj in object_list:
        line = json_dumps(obj) + '\n'
        fileobj.write(line.encode('utf-8'))
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


def get_job_id(raw_job_id):
    val = hmac.new(
        force_bytes(settings.SECRET_KEY),
        force_bytes(raw_job_id),
        digestmod=hashlib.sha1).hexdigest()
    safe_job_id = re.sub(r'[^a-zA-Z0-9\-_]', '_', raw_job_id)[:80]
    return f'{safe_job_id}_{val}'

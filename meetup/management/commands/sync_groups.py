import datetime
import logging

import boto3
import tqdm
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from insights.utils import json_records_gz
from meetup import api_client
from meetup.models import MeetupGroupFilter, MeetupGroup

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Sync meetup.com groups from API to database and to S3
    """
    help = 'Sync meetup.com groups from API to database and to S3'

    @atomic
    def handle(self, *args, **options):
        # collect groups to this dictionary, automatically eliminating
        # duplicates
        groups_dict = {}
        filters = tqdm.tqdm(list(MeetupGroupFilter.objects.get_active()))
        for filt in filters:
            filters.set_description(str(filt))
            groups = api_client.find_groups(
                category=filt.category.id,
                country=filt.location.country,
                location=filt.location.location)
            for g in groups:
                groups_dict[g.urlname] = g

        # create group models
        for group in groups_dict.values():
            MeetupGroup.from_api(group)

        # store data to S3
        now = datetime.datetime.utcnow()
        fileobj = json_records_gz(groups_dict.values())
        s3_key = f'groups/date={now:%F}/{now:%Y%m%d%H%M%S}.json.gz'
        client = boto3.client('s3')
        client.upload_fileobj(fileobj, settings.S3_BUCKET, s3_key)

import datetime
import logging

import tqdm
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from insights.utils import bigquery_upload, get_job_id
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

        # store data to bigquery
        now = datetime.datetime.utcnow()
        job_id = get_job_id(f'sync_groups_{now:%Y%m%d}')
        bigquery_upload(
            groups_dict.values(), 'groups', job_id=job_id, async=False)

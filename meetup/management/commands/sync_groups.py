import datetime
import logging
from argparse import ArgumentParser

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

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            '--skip-bigquery',
            action='store_true',
            help="If the flag is set, don't send data to BigQuery")

    @atomic
    def handle(self, *args, **options):
        # collect groups to this dictionary, automatically eliminating
        # duplicates
        groups_dict = {}
        filters = list(MeetupGroupFilter.objects.get_active())
        for i, filt in enumerate(filters):
            self.stdout.write(f'{i + 1:2d}/{len(filters)} Sync filter {filt}')
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
        if not options['skip_bigquery']:
            now = datetime.datetime.utcnow()
            job_id = get_job_id(f'sync_groups_{now:%Y%m%d}')
            bigquery_upload(
                groups_dict.values(), 'groups', job_id=job_id, async=False)

import datetime
import logging
import random
import time
import warnings
from argparse import ArgumentParser

import pytz
from django.core.management.base import BaseCommand
from django.db.transaction import atomic
from google.cloud.exceptions import Conflict
from insights.utils import bigquery_upload, get_job_id
from meetup import api_client
from meetup.models import MeetupGroup, MeetupGroupMember

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Sync meetup.com group members from API to database and to S3
    """
    help = 'Sync meetup.com group members from API to database and to S3'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            '--skip-bigquery',
            action='store_true',
            help="If the flag is set, don't send data to BigQuery")
        parser.add_argument(
            '--sleep', type=float, default=1,
            help='Sleep interval between syncing different groups (sec)'
        )

    def handle(self, *args, **options):
        skip_bigquery = options['skip_bigquery']
        sleep = options['sleep']
        groups = list(MeetupGroup.objects.members_update_required())
        for i, group in enumerate(groups):
            self.stdout.write(f'{i + 1:4d}/{len(groups)} Sync group {group}')
            self.sync_group(group, skip_bigquery)
            time.sleep(sleep)

    @atomic
    def sync_group(self, group: MeetupGroup, skip_bigquery: bool):
        # get the list of all group members
        members = list(api_client.group_members(group.urlname))
        for person in members:
            MeetupGroupMember.from_api(group, person)

        # store data to bigquery
        if not skip_bigquery:
            try:
                now = datetime.datetime.utcnow()
                job_id = get_job_id(f'sync_members_{group.urlname}_{now:%Y%m%d}')
                bigquery_upload(members, 'members', job_id=job_id, async=False)
            except Conflict as e:
                warnings.warn(str(e))

        # schedule next update tomorrow at random time
        group.members_next_update = get_random_tomorrow()
        group.save()


def get_random_tomorrow():
    tom = datetime.date.today() + datetime.timedelta(days=1)
    dt = datetime.datetime(tom.year, tom.month, tom.day)
    dt += datetime.timedelta(minutes=random.randint(60, 23 * 60))
    return pytz.utc.localize(dt)

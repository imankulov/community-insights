import datetime
import logging
import random
import time
import warnings

import pytz
import tqdm
from django.core.management.base import BaseCommand
from django.db.transaction import atomic
from google.cloud.exceptions import Conflict

from insights.utils import get_job_id, bigquery_upload
from meetup import api_client
from meetup.models import MeetupGroup, MeetupGroupMember

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Sync meetup.com group members from API to database and to S3
    """
    help = 'Sync meetup.com group members from API to database and to S3'

    def handle(self, *args, **options):
        groups = tqdm.tqdm(MeetupGroup.objects.members_update_required())
        for group in groups:
            groups.set_description(str(group))
            self.sync_group(group)

    @atomic
    def sync_group(self, group: MeetupGroup):
        # get the list of all group members
        members = list(api_client.group_members(group.urlname))
        for person in members:
            MeetupGroupMember.from_api(group, person)

        # store data to bigquery
        try:
            now = datetime.datetime.utcnow()
            job_id = get_job_id(f'sync_members_{group.urlname}_{now:%Y%m%d}')
            bigquery_upload(members, 'members', job_id=job_id, async=False)
        except Conflict as e:
            warnings.warn(str(e))

        # schedule next update tomorrow at random time
        group.members_next_update = get_random_tomorrow()
        group.save()
        time.sleep(1)


def get_random_tomorrow():
    tom = datetime.date.today() + datetime.timedelta(days=1)
    dt = datetime.datetime(tom.year, tom.month, tom.day)
    dt += datetime.timedelta(minutes=random.randint(60, 23 * 60))
    return pytz.utc.localize(dt)

import datetime
import logging
import random
import time

import boto3
import tqdm
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.transaction import atomic
from django.utils import timezone

from insights.utils import json_records_gz
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

        # store records into fileobj as set of JSON-encoded newline-separated
        fileobj = json_records_gz(members)

        # put that object to S3
        now = timezone.now()
        s3_key = f'members/group={group.urlname}/date={now:%F}/{group.urlname}_{now:%Y%m%d%H%M%S}.json.gz'
        client = boto3.client('s3')
        client.upload_fileobj(fileobj, settings.S3_BUCKET, s3_key)

        # schedule next update in about 24 hours
        minutes_diff = random.normalvariate(24 * 60, 2 * 60)
        group.members_next_update = now + datetime.timedelta(
            minutes=minutes_diff)
        group.save()
        time.sleep(1)

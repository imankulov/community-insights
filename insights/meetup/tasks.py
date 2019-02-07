import datetime
import random
import time
import warnings

import pytz
from celery import shared_task
from django.db.transaction import atomic
from google.cloud.exceptions import Conflict
from insights.meetup import api_client
from insights.meetup.models import (MeetupCategory, MeetupGroup,
                                    MeetupGroupFilter, MeetupGroupMember)
from insights.utils import bigquery_upload, get_job_id


@shared_task
def sync_categories():
    for obj in api_client.categories():
        MeetupCategory.from_api(obj)


@shared_task
def sync_groups():
    # collect groups to this dictionary, automatically eliminating
    # duplicates
    groups_dict = {}
    filters = list(MeetupGroupFilter.objects.get_active())
    for i, filt in enumerate(filters):
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
    bigquery_upload(groups_dict.values(), 'groups', job_id=job_id, async=False)


@shared_task
def sync_group_members():
    groups = list(MeetupGroup.objects.members_update_required())
    for i, group in enumerate(groups):
        sync_group(group)
        time.sleep(1)


@atomic
def sync_group(group: MeetupGroup):
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


def get_random_tomorrow():
    tom = datetime.date.today() + datetime.timedelta(days=1)
    dt = datetime.datetime(tom.year, tom.month, tom.day)
    dt += datetime.timedelta(minutes=random.randint(60, 23 * 60))
    return pytz.utc.localize(dt)

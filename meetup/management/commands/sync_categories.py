import logging

from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from meetup import api_client
from meetup.models import MeetupCategory

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Sync meetup.com categories from API to database
    """
    help = 'Sync meetup.com categories from meetup.com API to database'

    @atomic
    def handle(self, *args, **options):
        for obj in api_client.categories():
            MeetupCategory.from_api(obj)

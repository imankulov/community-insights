from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Create admin in a non-interactive mode
    """
    help = 'Create database'

    def handle(self, *args, **options):
        if User.objects.filter(username=settings.ADMIN_USERNAME).count() > 0:
            print(f'User {settings.ADMIN_USERNAME!r} already exists')
            return
        User.objects.create_superuser(settings.ADMIN_USERNAME,
                                      settings.ADMIN_EMAIL,
                                      settings.ADMIN_PASSWORD)

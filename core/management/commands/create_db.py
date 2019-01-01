import MySQLdb
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Create database
    """
    help = 'Create database'

    def handle(self, *args, **options):
        db_settings = settings.DATABASES['default']
        conn = MySQLdb.connect(
            host=db_settings['HOST'],
            port=db_settings['PORT'] or 3306,
            user=db_settings['USER'],
            passwd=db_settings['PASSWORD'])
        cur = conn.cursor()
        cur.execute(f'CREATE DATABASE {db_settings["NAME"]} '
                    f'CHARACTER SET utf8mb4 COLLATE utf8mb4_bin')
        conn.commit()

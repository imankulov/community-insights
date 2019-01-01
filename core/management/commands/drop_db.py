import MySQLdb
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Drop database
    """
    help = 'Drop database'

    def handle(self, *args, **options):
        db_settings = settings.DATABASES['default']
        conn = MySQLdb.connect(
            host=db_settings['HOST'],
            port=db_settings['PORT'] or 3306,
            user=db_settings['USER'],
            passwd=db_settings['PASSWORD'])
        cur = conn.cursor()
        cur.execute(f'DROP DATABASE {db_settings["NAME"]}')
        conn.commit()

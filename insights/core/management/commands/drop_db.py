import psycopg2
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Drop database
    """
    help = 'Drop database'

    def handle(self, *args, **options):
        db_settings = settings.DATABASES['default']
        conn = psycopg2.connect(**get_conn_kwargs())
        cur = conn.cursor()
        cur.execute(f'DROP DATABASE {db_settings["NAME"]}')
        conn.commit()

def get_conn_kwargs():
    db_settings = settings.DATABASES['default']
    kwargs = {}
    for key in ['HOST', 'PORT', 'USER', 'PASSWORD']:
        if db_settings[key]:
            kwargs[key.lower()] = db_settings[key]
    return kwargs

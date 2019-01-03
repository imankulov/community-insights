import psycopg2
from django.conf import settings
from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Create database
    """
    help = 'Create database'

    def handle(self, *args, **options):
        db_settings = settings.DATABASES['default']
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute(f'CREATE DATABASE {db_settings["NAME"]}')
        except psycopg2.ProgrammingError as e:
            raise CommandError(str(e))
        finally:
            conn.close()


def get_conn():
    db_settings = settings.DATABASES['default']
    kwargs = {}
    for key in ['HOST', 'PORT', 'USER', 'PASSWORD']:
        if db_settings[key]:
            kwargs[key.lower()] = db_settings[key]
    conn = psycopg2.connect(**kwargs)
    conn.autocommit = True
    return conn

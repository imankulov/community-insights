#!/usr/bin/env python
import sys
import os
import time
from subprocess import check_call


def cli():
    {
        'help': help,
        'sleep': sleep,
        'web': web,
        'cron': cron,
        'worker': worker,
        'manage': manage,
    }[sys.argv[1]]()


def help():
    raise SystemExit(
        f'Usage: {sys.argv[0]} web or {sys.argv[0]} <management-command>')


def sleep():
    while True:
        print('z-z-z-z-z!')
        time.sleep(3600)


def web():
    run("./manage.py", "migrate", "--noinput")
    run("./manage.py", "create_admin")
    run("./manage.py", "collectstatic", "--noinput")
    run("./manage.py", "diffsettings")
    exec_('gunicorn', 'insights.wsgi', '--bind', '0.0.0.0:8000')


def cron():
    args = (
        'celery -A insights beat -l info '
        '--scheduler django_celery_beat.schedulers:DatabaseScheduler'.split())
    exec_(*args)


def worker():
    args = (
        'celery -A insights worker -l info '
        '--scheduler django_celery_beat.schedulers:DatabaseScheduler'.split())
    exec_(*args)


def manage():
    args = ['./manage.py'] + sys.argv[2:]
    exec_(*args)


def run(*args):
    print('server $', ' '.join(args))
    return check_call(args)


def exec_(*args):
    print('server $', ' '.join(args))
    os.execlp(args[0], *args)


if __name__ == '__main__':
    cli()

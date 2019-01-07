#!/usr/bin/env python
import sys
import os
from subprocess import check_call


def run(*args):
    print('server $', ' '.join(args))
    return check_call(args)


if len(sys.argv) == 1:
    raise SystemExit(f'Usage: {sys.argv[0]} web or {sys.argv[0]} <management-command>')

if sys.argv[1] == 'web':
    run("./manage.py", "migrate", "--noinput")
    run("./manage.py", "create_admin")
    run("./manage.py", "collectstatic", "--noinput")
    run("./manage.py", "diffsettings")
    os.execlp('gunicorn', 'gunicorn', 'insights.wsgi', '--bind', '0.0.0.0:8000')

os.execlp("./manage.py", "./manage.py", *sys.argv[1:])

#!/usr/bin/env python
import sys
import os
from subprocess import check_call

if len(sys.argv) == 1:
    raise SystemExit(f'Usage: {sys.argv[0]} web or {sys.argv[0]} <management-command>')

if sys.argv[1] == 'web':
    check_call(["./manage.py", "migrate", "--noinput"])
    check_call(["./manage.py", "create_admin"])
    check_call(["./manage.py", "collectstatic", "--noinput"])
    check_call(["./manage.py", "diffsettings"])
    os.execlp('gunicorn', 'gunicorn', 'insights.wsgi', '--bind', '0.0.0.0:8000')

os.execlp("./manage.py", "./manage.py", *sys.argv[1:])

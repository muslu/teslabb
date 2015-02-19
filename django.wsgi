import os, sys

sys.path.append('/home/muslu/django/teslabb/')
sys.path.append('/home/muslu/django/teslabb/teslabb/')


os.environ['PYTHON_EGG_CACHE'] = '/home/muslu/.python-eggs'
os.environ['HTTPS'] = "on"

os.environ['DJANGO_SETTINGS_MODULE'] ='teslabb.settings'

import django.core.handlers.wsgi
application =django.core.handlers.wsgi.WSGIHandler()

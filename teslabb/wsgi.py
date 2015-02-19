import os
import sys

from django.core.handlers.wsgi import WSGIHandler




sys.path.append( '/home/muslu/django/teslabb/' )
sys.path.append( '/home/muslu/django/teslabb/teslabb/' )
os.environ['HTTPS'] = "on"
os.environ['DJANGO_SETTINGS_MODULE'] = 'teslabb.settings'
os.environ['PYTHON_EGG_CACHE'] = '/home/muslu/.python-eggs'
application = WSGIHandler( )

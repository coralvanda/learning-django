"""
WSGI config for learning_django project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

# add project to sys.path
sys.path.append("/var/www/learning-django")
# add virtual env site-packages to sys.path
sys.path.append("/var/www/learning-django/learning-django-env/Lib/site-packages")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "learning_django.settings")

application = get_wsgi_application()

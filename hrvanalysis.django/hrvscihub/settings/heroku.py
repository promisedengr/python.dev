"""
Production Settings for Heroku
"""

import environ

from hrvscihub.settings.base import *


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# False if not in os.environ
DEBUG = env('DEBUG')

# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')

# Cloudinary stuff
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUD_NAME'),
    'API_KEY':  env('API_KEY'),
    'API_SECRET':  env('API_SECRET'),
}

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

CELERY_BROKER_URL =  env('REDIS_TLS_URL')

# Parse database connection url strings like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
    # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
    'default': env.db(),
}
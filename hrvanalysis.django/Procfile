release: python manage.py migrate
web: gunicorn hrvscihub.wsgi
worker: celery -A hrvscihub worker --loglevel=info
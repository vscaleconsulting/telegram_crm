release: chmod u+x release.sh && ./release.sh;
web: gunicorn telegramleads.wsgi:application
worker: python manage.py runscript processes
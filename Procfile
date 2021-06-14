release: chmod u+x release.sh && ./release.sh
web: npm start &
web: gunicorn telegramleads.wsgi:application --bind 127.0.0.1:$DJANGO_PORT

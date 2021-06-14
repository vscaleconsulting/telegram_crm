# Webogram init
cd webogram
npm start &
cd ..

python manage.py makemigrations
python manage.py migrate

# python manage.py createsuperuser
# python manage.py shell < leads/check.py

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --noinput
gunicorn cdext.wsgi:application --bind 0.0.0.0:8000 $@
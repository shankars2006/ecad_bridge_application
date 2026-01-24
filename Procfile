web: python manage.py migrate --noinput && python manage.py create_initial_superuser && python manage.py collectstatic --noinput && gunicorn ecadbridge.wsgi:application --bind 0.0.0.0:$PORT

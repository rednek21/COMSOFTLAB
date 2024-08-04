#!/bin/sh
set -e

echo "Running migrations..."
python3 manage.py migrate
if [ $? -eq 0 ]; then
    echo "Migrations - OK"
else
    echo "Migrations failed"
    exit 1
fi

if [ "$DEBUG" = "False" ]
then
    python manage.py collectstatic --noinput
fi

if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

daphne -b 0.0.0.0 -p 8000 config.asgi:application

exec "$@"

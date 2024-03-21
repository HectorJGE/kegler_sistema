#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run all migrations
python manage.py migrate

# Compile all messages from .po files translations
python manage.py compilemessages

npm i
npm run build

# Collect static
python manage.py collectstatic --noinput

# start cron
/usr/sbin/crond start

exec "$@"
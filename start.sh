#!/bin/bash

# Set default port if not provided
export PORT=${PORT:-8000}

# Run database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start the application
exec gunicorn mswsite.wsgi:application --bind 0.0.0.0:$PORT --workers 3

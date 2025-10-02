#!/bin/bash

# Set default port if not provided
export PORT=${PORT:-8000}

# Run database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Initialize forecast data if needed
python -c "
from backend.initialize_cache import initialize_cache_if_needed
from backend.data_processor import get_processor
initialize_cache_if_needed()
processor = get_processor()
if not processor._is_cache_valid():
    print('Starting background data update...')
    processor.schedule_background_update()
"

# Start the application
exec gunicorn mswsite.wsgi:application --bind 0.0.0.0:$PORT --workers 3

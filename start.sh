#!/bin/bash

# Set default port if not provided
export PORT=${PORT:-8000}

# Run database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Initialize forecast data if needed
python -c "
from backend.data_processor import get_processor
processor = get_processor()
if not processor._is_cache_valid():
    print('Initializing forecast data...')
    processor.get_forecast_data()
    print('Forecast data initialized')
"

# Start the application
exec gunicorn mswsite.wsgi:application --bind 0.0.0.0:$PORT --workers 3

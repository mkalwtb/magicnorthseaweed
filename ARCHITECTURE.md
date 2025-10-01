# Magic North Seaweed - Architecture Overview

## Backend/Frontend Separation

The application has been refactored to separate backend data processing from frontend presentation:

### Backend (Data Processing)
- **Location**: `backend/` directory
- **Purpose**: Handles data scraping, processing, and storage
- **Components**:
  - `data_processor.py`: Core data processing and caching logic
  - `scheduler.py`: Automated scheduling for data updates
  - `data/`: Cache storage directory

### Frontend (Django Web App)
- **Location**: `forecast/` app and templates
- **Purpose**: Serves the web interface using cached data
- **Components**:
  - Django views that read from backend cache
  - Templates for HTML presentation
  - Static files and styling

## Data Flow

```
External APIs (Stormglass, Rijkswaterstaat)
    ↓
Backend Data Processor (every 12 hours)
    ↓
Cache Storage (backend/data/)
    ↓
Django Frontend (serves cached data)
    ↓
User Browser
```

## Key Features

### 1. Automated Data Updates
- **Frequency**: Every 12 hours
- **Process**: Background scheduler updates forecast data
- **Storage**: Cached in `backend/data/forecast_cache.pkl`

### 2. Cache Management
- **Validation**: Checks if cache is older than 12 hours
- **Fallback**: Generates fresh data if cache is invalid
- **Background Updates**: Non-blocking updates when cache expires

### 3. API Endpoints
- `/`: Main homepage
- `/week/`: Week overview
- `/spot/<name>/`: Individual spot forecasts
- `/health/`: Health check
- `/cache/status/`: Cache status information
- `/cache/refresh/`: Manual cache refresh

## Running the Application

### Development Mode

1. **Start Backend Scheduler** (separate terminal):
   ```bash
   python start_backend.py
   ```

2. **Start Django Frontend** (separate terminal):
   ```bash
   python manage.py runserver
   ```

### Production Mode

The Docker setup automatically:
1. Initializes forecast data on startup
2. Runs Django with gunicorn
3. Serves cached data to users

### Manual Operations

**Check cache status**:
```bash
curl http://localhost:8000/cache/status/
```

**Force cache refresh**:
```bash
curl -X POST http://localhost:8000/cache/refresh/
```

**Run scheduler manually**:
```bash
python manage.py run_scheduler
```

## Configuration

### Cache Settings
- **Duration**: 12 hours (configurable in `ForecastDataProcessor`)
- **Storage**: Pickle files in `backend/data/`
- **Metadata**: JSON files with cache information

### Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (False for production)
- `ALLOWED_HOSTS`: Allowed hostnames

## Benefits of This Architecture

1. **Performance**: Frontend serves cached data instantly
2. **Reliability**: Backend can update data without affecting frontend
3. **Scalability**: Can run backend and frontend on separate servers
4. **Maintainability**: Clear separation of concerns
5. **Monitoring**: Cache status and health check endpoints

## File Structure

```
magicnorthseaweed/
├── backend/                 # Backend data processing
│   ├── data_processor.py   # Core processing logic
│   ├── scheduler.py        # Automated scheduling
│   └── data/              # Cache storage
├── forecast/               # Django frontend app
│   ├── views.py           # Web endpoints
│   ├── templates/         # HTML templates
│   └── management/        # Django commands
├── data/                   # Original data modules
├── mswsite/               # Django project settings
├── start_backend.py       # Backend startup script
├── start.sh              # Production startup script
└── Dockerfile            # Container configuration
```

## Monitoring

### Logs
- **Backend**: `backend/scheduler.log`
- **Django**: Standard Django logging
- **Docker**: Container logs

### Health Checks
- **Application**: `GET /health/`
- **Cache Status**: `GET /cache/status/`
- **Manual Refresh**: `POST /cache/refresh/`

## Deployment

The application is designed to work with:
- **Railway**: Automatic deployment with Docker
- **Heroku**: Using Procfile and buildpacks
- **Docker**: Standalone container deployment
- **Traditional VPS**: Manual deployment with systemd services

## Troubleshooting

### Common Issues

1. **Cache not updating**: Check scheduler logs
2. **Import errors**: Ensure all dependencies are installed
3. **Port conflicts**: Check Railway PORT environment variable
4. **Data not loading**: Verify backend/data directory permissions

### Debug Commands

```bash
# Check cache status
python -c "from backend.data_processor import get_processor; print(get_processor().get_cache_status())"

# Force data refresh
python -c "from backend.data_processor import get_processor; get_processor().get_forecast_data(force_refresh=True)"

# Test scheduler
python backend/scheduler.py
```

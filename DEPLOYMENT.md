# Deployment Guide for Magic North Seaweed

This guide covers deploying the Django surf forecasting application to various platforms.

## Prerequisites

- Python 3.11+
- Git
- Virtual environment (recommended)

## Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd magicnorthseaweed
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

## Production Deployment

### Using Gunicorn + Nginx

1. **Install production dependencies:**
   ```bash
   pip install gunicorn whitenoise
   ```

2. **Set environment variables:**
   ```bash
   export SECRET_KEY="your-secret-key"
   export DEBUG=False
   export ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
   ```

3. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Run with Gunicorn:**
   ```bash
   gunicorn mswsite.wsgi:application --bind 0.0.0.0:8000
   ```

### Using Docker

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   RUN python manage.py collectstatic --noinput
   
   EXPOSE 8000
   
   CMD ["gunicorn", "mswsite.wsgi:application", "--bind", "0.0.0.0:8000"]
   ```

2. **Build and run:**
   ```bash
   docker build -t magicnorthseaweed .
   docker run -p 8000:8000 magicnorthseaweed
   ```

### Deploying to Heroku

1. **Install Heroku CLI**

2. **Login and create app:**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   ```

### Deploying to Railway

1. **Connect your GitHub repository to Railway:**
   - Go to [Railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Set environment variables in Railway dashboard:**
   - Go to your project → Variables tab
   - Add these variables:
     - `SECRET_KEY`: Your Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
     - `DEBUG`: False
     - `ALLOWED_HOSTS`: Your Railway domain (e.g., `your-app-name.railway.app`)
   - **Note:** Railway automatically sets the `PORT` environment variable - do not override it

3. **Deploy automatically on git push:**
   - Railway will automatically detect the Dockerfile
   - The app will build and deploy automatically
   - Check the deployment logs for any issues

4. **Access your deployed app:**
   - Railway will provide a URL like `https://your-app-name.railway.app`
   - The admin interface will be available at `https://your-app-name.railway.app/admin/`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | False |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | Required |
| `DATABASE_URL` | Database connection string (optional) | SQLite |

## Static Files

The application uses WhiteNoise to serve static files in production. Static files are automatically collected during deployment.

## Data Directory

The application requires a `data/` directory with:
- `stormglass/` - Cache directory for weather data
- `site_cache_content.pkl` - Cached site content
- `site_cache_state.json` - Cache state information

Make sure these directories exist and are writable by the application.

## Monitoring

- Check logs in `logs/django.log` for errors
- Monitor cache refresh status in the application
- Set up health checks for the `/` endpoint

## Security Considerations

- Never commit `.env` files
- Use strong secret keys in production
- Set `DEBUG=False` in production
- Configure proper `ALLOWED_HOSTS`
- Use HTTPS in production
- Regularly update dependencies

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **Cache issues**: Clear cache files in `data/` directory
3. **Static files not loading**: Run `collectstatic` command
4. **Database errors**: Run migrations with `python manage.py migrate`

### Logs

Check application logs for detailed error information:
- Django logs: `logs/django.log`
- Server logs: Check your deployment platform's logging system

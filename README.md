# Magic North Seaweed
AI-based surf forecasting and rating for the North Sea.

## Features
- Real-time surf forecasting for multiple North Sea locations
- AI-powered surf rating system
- Interactive web interface with forecast tables
- Automatic data caching and background updates
- Responsive design with subtle directional arrows

## Requirements
- Python 3.11+
- Virtual environment (recommended)

## Quick Start

### Local Development
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

4. **Run the Django server:**
   ```bash
   python manage.py runserver
   ```

5. **Visit the application:**
   Open http://localhost:8000 in your browser

### Using Docker
```bash
docker-compose up --build
```

## Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:
- Heroku deployment
- Railway deployment
- Docker deployment
- Production configuration

## Project Structure
- **`forecast/`** - Django web application
- **`data/`** - Data scrapers, processing, and ML models
- **`ai/`** - Machine learning models and training scripts
- **`mswsite/`** - Django project settings

## Data Sources
- Weather data from Stormglass API
- Tide data from Rijkswaterstaat
- Surf feedback from user submissions

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
This project is for educational and personal use.
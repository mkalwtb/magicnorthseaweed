"""
Pytest configuration and shared fixtures for Magic North Seaweed tests.
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
import pytest
from datetime import datetime, timedelta
import pytz

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'data'))

# Mock timezonefinder before importing stormglass
sys.modules['timezonefinder'] = Mock()
sys.modules['timezonefinder.TimezoneFinder'] = Mock()

# Mock timezone functionality
import pytz
sys.modules['pytz'] = Mock()
sys.modules['pytz.timezone'] = Mock()
sys.modules['pytz.timezone'].return_value = pytz.UTC

# Configure Django settings for testing
import os
import django
from django.conf import settings

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mswsite.settings')

# Configure Django settings for testing
if not settings.configured:
    django.setup()

# Configure test database
from django.test.utils import get_runner
from django.test import TestCase

# Import project modules
from data.spots import Spot, SpotInfo, SPOTS, find_spot
from data.models import Model, MODELS
from data.surffeedback import load, rename_columns, text_to_value
from data.plotting import angle_to_direction, index_interval
from data.webtables import get_color, height_label, round_off_rating
from data.stormglass import download_json, json_to_df, forecast
from alert import AlertFilter, AlertLog, content_generator, send_email, check


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_spot():
    """Create a mock spot for testing."""
    spot_info = SpotInfo(pier=0)
    return Spot(
        richting=290.0,
        name="TestSpot",
        lat=52.474773,
        long=4.535204,
        db_name="ZV",
        spot_info=spot_info
    )


@pytest.fixture
def sample_weather_data():
    """Sample weather data for testing."""
    dates = pd.date_range(start='2024-01-01', periods=24, freq='H')
    return pd.DataFrame({
        'waveHeight': np.random.uniform(0.5, 3.0, 24),
        'wavePeriod': np.random.uniform(4.0, 12.0, 24),
        'waveDirection': np.random.uniform(0, 360, 24),
        'windSpeed': np.random.uniform(2.0, 15.0, 24),
        'windDirection': np.random.uniform(0, 360, 24),
        'currentSpeed': np.random.uniform(0.1, 2.0, 24),
        'windWaveHeight': np.random.uniform(0.2, 1.5, 24),
        'NAP': np.random.uniform(-1.0, 2.0, 24),
        'rating': np.random.uniform(1, 10, 24),
        'hoogte-v2': np.random.uniform(0, 7, 24),
        'hoog': np.random.uniform(0, 3, 24),
        'clean': np.random.uniform(0, 3, 24),
        'krachtig': np.random.uniform(0, 3, 24),
        'stijl': np.random.uniform(0, 3, 24),
        'stroming': np.random.uniform(0, 3, 24),
        'windy': np.random.uniform(0, 3, 24)
    }, index=dates)


@pytest.fixture
def sample_feedback_data():
    """Sample surf feedback data for testing."""
    return pd.DataFrame({
        'spot': ['ZV', 'ZV', 'Schev', 'Noordwijk'],
        'rating': [7.5, 8.0, 6.5, 9.0],
        'hoogte-v2': [2, 3, 1, 4],
        'clean': [2, 3, 1, 3],
        'krachtig': [1, 2, 0, 3],
        'stijl': [2, 3, 1, 3],
        'stroming': [1, 2, 0, 2],
        'windy': [0, 1, 2, 0],
        'Datum': ['01-01-2024', '02-01-2024', '03-01-2024', '04-01-2024'],
        'Start tijd': ['10:00:00', '11:00:00', '12:00:00', '13:00:00'],
        'Eind tijd': ['12:00:00', '13:00:00', '14:00:00', '15:00:00']
    })


@pytest.fixture
def mock_stormglass_response():
    """Mock Stormglass API response."""
    return {
        'hours': [
            {
                'time': '2024-01-01T00:00:00+00:00',
                'waveHeight': {'icon': 1.5, 'sg': 1.5},
                'wavePeriod': {'icon': 8.0, 'sg': 8.0},
                'waveDirection': {'icon': 270.0, 'sg': 270.0},
                'windSpeed': {'icon': 5.0, 'sg': 5.0},
                'windDirection': {'icon': 180.0, 'sg': 180.0},
                'currentSpeed': {'sg': 0.5},
                'windWaveHeight': {'icon': 0.8, 'sg': 0.8}
            },
            {
                'time': '2024-01-01T01:00:00+00:00',
                'waveHeight': {'icon': 1.8, 'sg': 1.8},
                'wavePeriod': {'icon': 9.0, 'sg': 9.0},
                'waveDirection': {'icon': 275.0, 'sg': 275.0},
                'windSpeed': {'icon': 6.0, 'sg': 6.0},
                'windDirection': {'icon': 185.0, 'sg': 185.0},
                'currentSpeed': {'sg': 0.6},
                'windWaveHeight': {'icon': 1.0, 'sg': 1.0}
            }
        ]
    }


@pytest.fixture
def mock_tide_response():
    """Mock tide API response."""
    return {
        'data': [
            {'time': '2024-01-01T00:00:00+00:00', 'value': 0.5},
            {'time': '2024-01-01T01:00:00+00:00', 'value': 0.6}
        ]
    }


@pytest.fixture
def mock_model():
    """Create a mock XGBoost model for testing."""
    model = Mock()
    model.predict.return_value = np.array([7.5, 8.0, 6.5])
    return model


@pytest.fixture
def sample_alert_filter():
    """Create a sample alert filter for testing."""
    spot = SPOTS[0]  # Use first spot from SPOTS
    return AlertFilter(
        spot=spot,
        rating_threshold=7,
        email="test@example.com",
        ID=1
    )


@pytest.fixture(autouse=True)
def mock_stormglass_calls():
    """Mock all Stormglass API calls to avoid external dependencies."""
    with patch('data.stormglass.download_json') as mock_download, \
         patch('data.stormglass.download_weather_and_tide') as mock_weather_tide, \
         patch('data.stormglass.forecast') as mock_forecast:
        
        # Configure mocks to return sample data
        mock_download.return_value = {
            'hours': [{'time': '2024-01-01T00:00:00+00:00', 'waveHeight': {'icon': 1.5}}]
        }
        mock_weather_tide.return_value = pd.DataFrame({
            'waveHeight': [1.5, 1.8],
            'wavePeriod': [8.0, 9.0]
        }, index=pd.date_range('2024-01-01', periods=2, freq='H'))
        mock_forecast.return_value = pd.DataFrame({
            'waveHeight': [1.5, 1.8],
            'wavePeriod': [8.0, 9.0]
        }, index=pd.date_range('2024-01-01', periods=2, freq='H'))
        
        yield {
            'download_json': mock_download,
            'download_weather_and_tide': mock_weather_tide,
            'forecast': mock_forecast
        }


@pytest.fixture(autouse=True)
def mock_file_operations():
    """Mock file operations to avoid creating actual files during tests."""
    with patch('builtins.open', create=True) as mock_open, \
         patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.is_file') as mock_is_file:
        
        mock_exists.return_value = False
        mock_is_file.return_value = False
        mock_open.return_value.__enter__.return_value = Mock()
        
        yield {
            'open': mock_open,
            'exists': mock_exists,
            'is_file': mock_is_file
        }


@pytest.fixture(autouse=True)
def mock_model_loading():
    """Mock model loading to avoid file dependencies."""
    with patch('data.models.Model._load_model') as mock_load_model:
        # Create a mock XGBoost model
        mock_xgb_model = Mock()
        mock_xgb_model.predict.return_value = np.array([7.5, 8.0, 6.5])
        mock_load_model.return_value = mock_xgb_model
        
        yield mock_load_model

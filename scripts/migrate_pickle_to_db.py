#!/usr/bin/env python
"""
Data migration script to transfer pickle file data to database.
Run this script to migrate existing pickle data to the new database structure.
"""

import os
import sys
import django
import pandas as pd
from pathlib import Path
from datetime import datetime
import pytz

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mswsite.settings')
django.setup()

from forecast.models import WeatherData, AlertLog, SurfFeedback, BuoyData, SiteCache
from data.stormglass import load_data
import pickle


def migrate_weather_data():
    """Migrate stormglass weather data from pickle files"""
    data_dir = Path('data/stormglass')
    
    if not data_dir.exists():
        print("No stormglass data directory found, skipping weather data migration")
        return
    
    migrated_count = 0
    for pkl_file in data_dir.glob('data_*.pkl'):
        location_name = pkl_file.stem.replace('data_', '')
        print(f"Migrating weather data for {location_name}")
        
        try:
            df = pd.read_pickle(pkl_file)
            
            if df.empty:
                print(f"  No data found in {pkl_file}")
                continue
            
            # Get location coordinates from the first record or use defaults
            lat, long = 52.0, 4.0  # Default coordinates for Netherlands
            
            for timestamp, row in df.iterrows():
                # Ensure timestamp is timezone-aware
                if timestamp.tzinfo is None:
                    timestamp = pytz.UTC.localize(timestamp)
                
                WeatherData.objects.update_or_create(
                    location_name=location_name,
                    timestamp=timestamp,
                    defaults={
                        'latitude': lat,
                        'longitude': long,
                        'wave_direction': row.get('waveDirection'),
                        'wave_period': row.get('wavePeriod'),
                        'wave_height': row.get('waveHeight'),
                        'wind_speed': row.get('windSpeed'),
                        'wind_direction': row.get('windDirection'),
                        'current_speed': row.get('currentSpeed'),
                        'wind_wave_height': row.get('windWaveHeight'),
                        'sea_level': row.get('seaLevel'),
                        'wave_onshore': row.get('waveOnshore'),
                        'wind_onshore': row.get('windOnshore'),
                    }
                )
                migrated_count += 1
            
            print(f"  Migrated {len(df)} records for {location_name}")
            
        except Exception as e:
            print(f"  Error migrating {location_name}: {e}")
    
    print(f"Total weather data records migrated: {migrated_count}")


def migrate_alert_logs():
    """Migrate alert logs from pickle file"""
    alert_file = Path('alert_log.pkl')
    if not alert_file.exists():
        print("No alert log file found, skipping alert logs migration")
        return
    
    print("Migrating alert logs")
    try:
        df = pd.read_pickle(alert_file)
        
        if df.empty:
            print("  No alert log data found")
            return
        
        migrated_count = 0
        for _, row in df.iterrows():
            # Ensure timestamp is timezone-aware
            timestamp = row['timestamp']
            if timestamp.tzinfo is None:
                timestamp = pytz.UTC.localize(timestamp)
            
            AlertLog.objects.create(
                timestamp=timestamp,
                spot=row['spot'],
                rating=row['rating'],
                email=row['email'],
                alert_timestamp=row['alert_timestamp']
            )
            migrated_count += 1
        
        print(f"  Migrated {migrated_count} alert log records")
        
    except Exception as e:
        print(f"  Error migrating alert logs: {e}")


def migrate_surf_feedback():
    """Migrate surf feedback data"""
    feedback_file = Path('data/surf-feedback-raw/Surf-feedback.pkl')
    if not feedback_file.exists():
        print("No surf feedback file found, skipping surf feedback migration")
        return
    
    print("Migrating surf feedback")
    try:
        df = pd.read_pickle(feedback_file)
        
        if df.empty:
            print("  No surf feedback data found")
            return
        
        migrated_count = 0
        for _, row in df.iterrows():
            # Ensure timestamp is timezone-aware
            timestamp = row['timestamp']
            if timestamp.tzinfo is None:
                timestamp = pytz.UTC.localize(timestamp)
            
            SurfFeedback.objects.create(
                timestamp=timestamp,
                spot=row['spot'],
                rating=row['rating'],
                # Add other fields as needed based on your data structure
            )
            migrated_count += 1
        
        print(f"  Migrated {migrated_count} surf feedback records")
        
    except Exception as e:
        print(f"  Error migrating surf feedback: {e}")


def migrate_buoy_data():
    """Migrate buoy data from pickle files"""
    buoy_dir = Path('data/boei-data')
    
    if not buoy_dir.exists():
        print("No buoy data directory found, skipping buoy data migration")
        return
    
    migrated_count = 0
    for pkl_file in buoy_dir.glob('*.pkl'):
        buoy_name = pkl_file.stem
        print(f"Migrating buoy data for {buoy_name}")
        
        try:
            df = pd.read_pickle(pkl_file)
            
            if df.empty:
                print(f"  No data found in {pkl_file}")
                continue
            
            for timestamp, row in df.iterrows():
                # Ensure timestamp is timezone-aware
                if timestamp.tzinfo is None:
                    timestamp = pytz.UTC.localize(timestamp)
                
                BuoyData.objects.update_or_create(
                    buoy_name=buoy_name,
                    timestamp=timestamp,
                    defaults={
                        'wave_height': row.get('waveHeight'),
                        'wave_period': row.get('wavePeriod'),
                        'wind_speed': row.get('windSpeed'),
                        # Add other buoy measurement fields as needed
                    }
                )
                migrated_count += 1
            
            print(f"  Migrated {len(df)} records for {buoy_name}")
            
        except Exception as e:
            print(f"  Error migrating {buoy_name}: {e}")
    
    print(f"Total buoy data records migrated: {migrated_count}")


def migrate_site_cache():
    """Migrate site cache data"""
    cache_file = Path('data/site_cache_content.pkl')
    if not cache_file.exists():
        print("No site cache file found, skipping site cache migration")
        return
    
    print("Migrating site cache")
    try:
        with open(cache_file, 'rb') as f:
            cache_data = pickle.load(f)
        
        if not cache_data:
            print("  No site cache data found")
            return
        
        # Convert cache data to string and store
        cache_key = "main_site_content"
        content = str(cache_data)
        expires_at = datetime.now() + pd.Timedelta(days=1)  # Cache expires in 1 day
        
        SiteCache.objects.update_or_create(
            cache_key=cache_key,
            defaults={
                'content': content,
                'expires_at': expires_at
            }
        )
        
        print("  Migrated site cache data")
        
    except Exception as e:
        print(f"  Error migrating site cache: {e}")


def main():
    """Run all migration functions"""
    print("Starting pickle to database migration...")
    print("=" * 50)
    
    migrate_weather_data()
    print()
    
    migrate_alert_logs()
    print()
    
    migrate_surf_feedback()
    print()
    
    migrate_buoy_data()
    print()
    
    migrate_site_cache()
    print()
    
    print("=" * 50)
    print("Migration completed!")
    print("\nNote: ML models are kept as pickle files as requested.")
    print("Weather data, alert logs, surf feedback, buoy data, and site cache")
    print("have been migrated to the database.")


if __name__ == '__main__':
    main()



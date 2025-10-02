"""
Backend data processor for surf forecasting.
Handles data scraping, processing, and storage.
"""

import os
import sys
import json
import pickle
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from data.models import MODELS
from data.spots import SPOTS
from data import webtables
from data.plotting import website_folder


class ForecastDataProcessor:
    """Handles forecast data processing and storage."""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or PROJECT_ROOT / "backend" / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = self.data_dir / "forecast_cache.pkl"
        self.metadata_file = self.data_dir / "forecast_metadata.json"
        
        # Cache settings
        self.cache_duration_hours = 12
        self._cache_lock = threading.Lock()
        
    def _load_metadata(self) -> dict:
        """Load cache metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_updated": None, "next_update": None}
    
    def _save_metadata(self, metadata: dict):
        """Save cache metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid."""
        metadata = self._load_metadata()
        if not metadata.get("last_updated"):
            return False
        
        last_updated = datetime.fromisoformat(metadata["last_updated"])
        return datetime.now() - last_updated < timedelta(hours=self.cache_duration_hours)
    
    def _get_next_update_time(self) -> datetime:
        """Get the next scheduled update time."""
        metadata = self._load_metadata()
        if metadata.get("next_update"):
            return datetime.fromisoformat(metadata["next_update"])
        
        # If no next update time, schedule one for 12 hours from now
        return datetime.now() + timedelta(hours=self.cache_duration_hours)
    
    def _generate_forecast_data(self) -> dict:
        """Generate fresh forecast data."""
        print("Generating fresh forecast data...")
        
        # Ensure stormglass cache directory exists with proper permissions
        stormglass_dir = PROJECT_ROOT / "data" / "stormglass"
        stormglass_dir.mkdir(parents=True, exist_ok=True)
        
        # Change to data directory for relative path resolution
        current_dir = os.getcwd()
        data_dir = PROJECT_ROOT / "data"
        os.chdir(data_dir)
        
        # Ensure stormglass subdirectory exists in current working directory
        local_stormglass_dir = Path("stormglass")
        local_stormglass_dir.mkdir(exist_ok=True)
        
        try:
            datas = []
            spot_tables = {}
            spot_widgets = {}
            
            for spot in SPOTS:
                print(f"Processing {spot.name}...")
                try:
                    # Always use fresh data (cache=False)
                    data = spot.surf_rating(cache=False, models=MODELS)
                    data.name = spot.name
                    datas.append(data)
                    
                    # Generate HTML tables
                    spot_tables[spot.name] = webtables.table_per_day(data, spot, webtables.table_html)
                    spot_widgets[spot.name] = webtables.table_html_simple(data, spot)
                    
                except Exception as e:
                    print(f"Error processing {spot.name}: {e}")
                    # Continue with other spots even if one fails
                    continue
            
            if not datas:
                raise Exception("No forecast data could be generated for any spots")
            
            # Generate week overview
            week_overview_html = webtables.weekoverzicht(datas)
            
            return {
                "week_overview": week_overview_html,
                "spot_tables": spot_tables,
                "spot_widgets": spot_widgets,
                "generated_at": datetime.now().isoformat(),
                "spots_processed": [data.name for data in datas]
            }
            
        finally:
            os.chdir(current_dir)
    
    def _save_forecast_data(self, data: dict):
        """Save forecast data to cache."""
        with self._cache_lock:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            # Update metadata
            now = datetime.now()
            next_update = now + timedelta(hours=self.cache_duration_hours)
            
            metadata = {
                "last_updated": now.isoformat(),
                "next_update": next_update.isoformat(),
                "cache_duration_hours": self.cache_duration_hours,
                "spots_count": len(data.get("spots_processed", [])),
                "data_size_bytes": len(pickle.dumps(data))
            }
            
            self._save_metadata(metadata)
            print(f"Forecast data cached. Next update: {next_update}")
    
    def _load_forecast_data(self) -> dict:
        """Load forecast data from cache."""
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading cached data: {e}")
            return None
    
    def get_forecast_data(self, force_refresh: bool = False) -> dict:
        """Get forecast data, using cache if valid."""
        cached_data = self._load_forecast_data()
        
        if force_refresh or not self._is_cache_valid():
            if cached_data and not force_refresh:
                # If we have cached data and this isn't a forced refresh,
                # start background update and return cached data immediately
                print("Cache expired, starting background update...")
                self.schedule_background_update()
                return cached_data
            else:
                # Force refresh or no cached data - generate synchronously
                try:
                    data = self._generate_forecast_data()
                    self._save_forecast_data(data)
                    return data
                except Exception as e:
                    print(f"Error generating fresh data: {e}")
                    if cached_data:
                        print("Falling back to cached data")
                        return cached_data
                    else:
                        raise e
        else:
            # Use cached data
            if cached_data:
                print("Using cached forecast data")
                return cached_data
            else:
                # No cache exists, generate fresh data
                data = self._generate_forecast_data()
                self._save_forecast_data(data)
                return data
    
    def get_cache_status(self) -> dict:
        """Get information about the current cache status."""
        metadata = self._load_metadata()
        is_valid = self._is_cache_valid()
        
        return {
            "cache_valid": is_valid,
            "last_updated": metadata.get("last_updated"),
            "next_update": metadata.get("next_update"),
            "cache_duration_hours": self.cache_duration_hours,
            "cache_file_exists": self.cache_file.exists(),
            "cache_size_bytes": self.cache_file.stat().st_size if self.cache_file.exists() else 0
        }
    
    def schedule_background_update(self):
        """Schedule a background update if cache is expired."""
        # Check if there's already an update running
        if hasattr(self, '_update_thread') and self._update_thread and self._update_thread.is_alive():
            print("Background update already in progress")
            return self._update_thread
            
        def background_update():
            try:
                print("Starting background forecast update...")
                data = self._generate_forecast_data()
                self._save_forecast_data(data)
                print("Background forecast update completed")
            except Exception as e:
                print(f"Background update failed: {e}")
            finally:
                self._update_thread = None
        
        self._update_thread = threading.Thread(target=background_update, daemon=True)
        self._update_thread.start()
        return self._update_thread


# Global processor instance
_processor = None

def get_processor() -> ForecastDataProcessor:
    """Get the global forecast data processor instance."""
    global _processor
    if _processor is None:
        _processor = ForecastDataProcessor()
    return _processor


if __name__ == "__main__":
    # Test the processor
    processor = ForecastDataProcessor()
    
    print("Cache status:")
    status = processor.get_cache_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\nGetting forecast data...")
    data = processor.get_forecast_data()
    print(f"Retrieved data for {len(data.get('spots_processed', []))} spots")

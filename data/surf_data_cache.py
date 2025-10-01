"""
Surf Data Cache Service

This module provides a caching service for surf rating forecast data that refreshes
every 12 hours. It separates data generation from page rendering, allowing for
on-demand page generation while keeping the expensive data computation cached.
"""

import sys
import os
import threading
import time
import json
import pickle
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.models import MODELS
from data.spots import SPOTS


class SurfDataCache:
    """
    Caches surf rating forecast data and refreshes it every 12 hours.
    Provides thread-safe access to cached data.
    """
    
    CACHE_MAX_AGE_SECONDS = 60 * 60 * 12  # 12 hours
    CACHE_STATE_FILE = Path(__file__).resolve().parent / 'surf_cache_state.json'
    CACHE_DATA_FILE = Path(__file__).resolve().parent / 'surf_cache_data.pkl'
    
    def __init__(self):
        self._lock = threading.Lock()
        self._last_refresh_thread = None
        self._data_dir = Path(__file__).resolve().parent
        
    def _get_last_update_ts(self) -> float:
        """Get the timestamp of the last data refresh."""
        if self.CACHE_STATE_FILE.is_file():
            try:
                with open(self.CACHE_STATE_FILE, 'r') as f:
                    state = json.load(f)
                    return float(state.get('last_update_ts', 0))
            except Exception:
                return 0.0
        return 0.0
    
    def _set_last_update_ts(self, ts: float):
        """Set the timestamp of the last data refresh."""
        with open(self.CACHE_STATE_FILE, 'w') as f:
            json.dump({'last_update_ts': ts}, f)
    
    def _load_cached_data(self) -> Optional[Dict[str, Any]]:
        """Load cached surf data from disk."""
        if self.CACHE_DATA_FILE.is_file():
            try:
                with open(self.CACHE_DATA_FILE, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                return None
        return None
    
    def _save_cached_data(self, data: Dict[str, Any]):
        """Save surf data to cache."""
        with open(self.CACHE_DATA_FILE, 'wb') as f:
            pickle.dump(data, f)
    
    def _generate_surf_data(self) -> Dict[str, Any]:
        """
        Generate fresh surf rating data for all spots.
        This is the expensive operation that we want to cache.
        """
        # Ensure we're in the data directory for stormglass cache resolution
        old_cwd = Path.cwd()
        os.chdir(self._data_dir)
        
        try:
            # Ensure stormglass cache directory exists
            (self._data_dir / 'stormglass').mkdir(exist_ok=True)
            
            surf_data = {}
            
            for spot in SPOTS:
                # Generate fresh surf rating data (no cache)
                data = spot.surf_rating(cache=False, models=MODELS)
                data.name = spot.name
                surf_data[spot.name] = {
                    'data': data,
                    'spot': spot,
                    'generated_at': time.time()
                }
            
            return surf_data
            
        finally:
            os.chdir(old_cwd)
    
    def _refresh_data_background(self):
        """Refresh data in background thread."""
        try:
            print(f"[SurfDataCache] Starting background data refresh at {datetime.now()}")
            data = self._generate_surf_data()
            self._save_cached_data(data)
            self._set_last_update_ts(time.time())
            print(f"[SurfDataCache] Background data refresh completed at {datetime.now()}")
        except Exception as e:
            print(f"[SurfDataCache] Background refresh failed: {e}")
            # Keep old cache on error
    
    def get_surf_data(self) -> Dict[str, Any]:
        """
        Get cached surf data. If data is older than 12 hours, trigger background refresh.
        If no cache exists, generate synchronously.
        
        Returns:
            Dict mapping spot names to their surf data
        """
        with self._lock:
            last_ts = self._get_last_update_ts()
            age = time.time() - last_ts
            data = self._load_cached_data()
            
            if data is None:
                # First-time compute synchronously
                print(f"[SurfDataCache] No cache found, generating data synchronously")
                data = self._generate_surf_data()
                self._save_cached_data(data)
                self._set_last_update_ts(time.time())
                return data
            
            if age > self.CACHE_MAX_AGE_SECONDS:
                # Check if background refresh is already running
                if self._last_refresh_thread is None or not self._last_refresh_thread.is_alive():
                    print(f"[SurfDataCache] Cache is {age/3600:.1f} hours old, starting background refresh")
                    self._last_refresh_thread = threading.Thread(
                        target=self._refresh_data_background, 
                        daemon=True
                    )
                    self._last_refresh_thread.start()
                else:
                    print(f"[SurfDataCache] Background refresh already in progress")
            
            return data
    
    def get_spot_data(self, spot_name: str) -> Optional[Dict[str, Any]]:
        """
        Get surf data for a specific spot.
        
        Args:
            spot_name: Name of the spot to get data for
            
        Returns:
            Dict with 'data' and 'spot' keys, or None if spot not found
        """
        surf_data = self.get_surf_data()
        return surf_data.get(spot_name)
    
    def force_refresh(self):
        """Force an immediate refresh of all surf data."""
        with self._lock:
            print(f"[SurfDataCache] Force refresh requested at {datetime.now()}")
            data = self._generate_surf_data()
            self._save_cached_data(data)
            self._set_last_update_ts(time.time())
            return data
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the current cache state."""
        last_ts = self._get_last_update_ts()
        age = time.time() - last_ts
        data = self._load_cached_data()
        
        return {
            'last_update': datetime.fromtimestamp(last_ts).isoformat() if last_ts > 0 else None,
            'age_hours': age / 3600,
            'is_stale': age > self.CACHE_MAX_AGE_SECONDS,
            'has_data': data is not None,
            'spots_cached': list(data.keys()) if data else []
        }


# Global instance
_surf_cache = SurfDataCache()


def get_surf_data() -> Dict[str, Any]:
    """Get cached surf data for all spots."""
    return _surf_cache.get_surf_data()


def get_spot_data(spot_name: str) -> Optional[Dict[str, Any]]:
    """Get surf data for a specific spot."""
    return _surf_cache.get_spot_data(spot_name)


def force_refresh_surf_data() -> Dict[str, Any]:
    """Force an immediate refresh of all surf data."""
    return _surf_cache.force_refresh()


def get_cache_info() -> Dict[str, Any]:
    """Get information about the current cache state."""
    return _surf_cache.get_cache_info()


if __name__ == '__main__':
    # Test the cache
    print("Testing SurfDataCache...")
    info = get_cache_info()
    print(f"Cache info: {info}")
    
    data = get_surf_data()
    print(f"Loaded data for spots: {list(data.keys())}")
    
    # Test individual spot access
    spot_data = get_spot_data('ZV')
    if spot_data:
        print(f"ZV data shape: {spot_data['data'].shape}")
        print(f"ZV data columns: {list(spot_data['data'].columns)}")

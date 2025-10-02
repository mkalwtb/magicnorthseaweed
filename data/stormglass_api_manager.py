"""
Optimized StormGlass API manager with intelligent key rotation and usage tracking.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
import threading
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class ApiKeyUsage:
    """Track usage for a single API key."""
    key: str
    daily_quota: int = 10
    requests_today: int = 0
    last_reset_date: str = ""
    last_used: Optional[str] = None
    total_requests: int = 0
    
    def reset_if_new_day(self):
        """Reset daily counter if it's a new day."""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_reset_date != today:
            self.requests_today = 0
            self.last_reset_date = today
    
    def can_make_request(self) -> bool:
        """Check if this key can make another request today."""
        self.reset_if_new_day()
        return self.requests_today < self.daily_quota
    
    def record_request(self, cost: int = 1):
        """Record a successful API request."""
        self.reset_if_new_day()
        self.requests_today += cost
        self.total_requests += cost
        self.last_used = datetime.now().isoformat()


class StormGlassApiManager:
    """Manages StormGlass API keys with intelligent rotation and usage tracking."""
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path("data/stormglass")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.usage_file = self.cache_dir / "api_usage.json"
        self.lock = threading.Lock()
        
        # API keys from the original stormglass.py
        self.api_keys = [
            '1feeb6a8-5bc9-11ee-a26f-0242ac130002-1feeb702-5bc9-11ee-a26f-0242ac130002',
            '5bf98f1a-2979-11ee-8d52-0242ac130002-5bf98f88-2979-11ee-8d52-0242ac130002',
            'a5396776-5d64-11ee-8b7f-0242ac130002-a53967da-5d64-11ee-8b7f-0242ac130002',
            '25c9c3a8-5e29-11ee-92e6-0242ac130002-25c9c40c-5e29-11ee-92e6-0242ac130002',
            'e2f68d4e-5eab-11ee-8d52-0242ac130002-e2f68e2a-5eab-11ee-8d52-0242ac130002',
            '9bb1648a-5ee8-11ee-a26f-0242ac130002-9bb164e4-5ee8-11ee-a26f-0242ac130002'
        ]
        
        self.key_usage = self._load_usage_data()
        
    def _load_usage_data(self) -> Dict[str, ApiKeyUsage]:
        """Load API usage data from persistent storage."""
        usage_data = {}
        
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
                    for key_id, usage_dict in data.items():
                        usage_data[key_id] = ApiKeyUsage(**usage_dict)
            except Exception as e:
                print(f"Warning: Could not load API usage data: {e}")
        
        # Initialize any missing keys
        for i, key in enumerate(self.api_keys):
            key_id = f"key_{i}"
            if key_id not in usage_data:
                usage_data[key_id] = ApiKeyUsage(key=key)
        
        return usage_data
    
    def _save_usage_data(self):
        """Save API usage data to persistent storage."""
        try:
            data = {key_id: asdict(usage) for key_id, usage in self.key_usage.items()}
            with open(self.usage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save API usage data: {e}")
    
    def get_best_key(self) -> Tuple[str, str]:
        """
        Get the best available API key for making a request.
        Returns (key_id, api_key) or raises exception if no keys available.
        """
        with self.lock:
            # Reset daily counters if needed
            for usage in self.key_usage.values():
                usage.reset_if_new_day()
            
            # Find keys that can still make requests today
            available_keys = [
                (key_id, usage) for key_id, usage in self.key_usage.items()
                if usage.can_make_request()
            ]
            
            if not available_keys:
                # Check if we can reset any keys (new day)
                today = datetime.now().strftime("%Y-%m-%d")
                reset_keys = []
                for key_id, usage in self.key_usage.items():
                    if usage.last_reset_date != today:
                        usage.reset_if_new_day()
                        if usage.can_make_request():
                            reset_keys.append((key_id, usage))
                
                if reset_keys:
                    available_keys = reset_keys
                else:
                    raise Exception("All API keys have reached their daily limit. Please wait until tomorrow.")
            
            # Sort by usage (least used first) and last used time
            available_keys.sort(key=lambda x: (x[1].requests_today, x[1].last_used or ""))
            
            key_id, usage = available_keys[0]
            return key_id, usage.key
    
    def record_successful_request(self, key_id: str, response_meta: Dict):
        """
        Record a successful API request and update usage statistics.
        
        Args:
            key_id: The key identifier that was used
            response_meta: The 'meta' section from StormGlass API response
        """
        with self.lock:
            if key_id in self.key_usage:
                usage = self.key_usage[key_id]
                
                # Extract cost and quota from response
                cost = response_meta.get('cost', 1)
                daily_quota = response_meta.get('dailyQuota', 10)
                request_count = response_meta.get('requestCount', usage.requests_today + cost)
                
                # Update usage data
                usage.daily_quota = daily_quota
                usage.record_request(cost)
                
                # If the API response includes current request count, use it
                if 'requestCount' in response_meta:
                    usage.requests_today = request_count
                
                self._save_usage_data()
                
                print(f"API Key {key_id}: Used {cost} requests, {usage.requests_today}/{usage.daily_quota} today")
    
    def get_usage_summary(self) -> Dict:
        """Get a summary of API usage across all keys."""
        with self.lock:
            summary = {
                'total_keys': len(self.api_keys),
                'keys_available': 0,
                'total_requests_today': 0,
                'total_quota_today': 0,
                'key_details': {}
            }
            
            for key_id, usage in self.key_usage.items():
                usage.reset_if_new_day()
                
                summary['total_requests_today'] += usage.requests_today
                summary['total_quota_today'] += usage.daily_quota
                
                if usage.can_make_request():
                    summary['keys_available'] += 1
                
                summary['key_details'][key_id] = {
                    'requests_today': usage.requests_today,
                    'daily_quota': usage.daily_quota,
                    'available': usage.can_make_request(),
                    'last_used': usage.last_used,
                    'total_requests': usage.total_requests
                }
            
            return summary
    
    def make_request(self, url: str, params: Dict, timeout: int = 30) -> Tuple[Dict, str]:
        """
        Make an optimized API request using the best available key.
        
        Returns:
            Tuple of (response_json, key_id_used)
        """
        key_id, api_key = self.get_best_key()
        
        headers = {'Authorization': api_key}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            json_data = response.json()
            
            # Check for API errors
            if "errors" in json_data:
                error_msg = json_data["errors"]
                if isinstance(error_msg, dict) and "key" in error_msg:
                    error_msg = error_msg["key"]
                raise Exception(f"StormGlass API Error: {error_msg}")
            
            # Record successful request
            if "meta" in json_data:
                self.record_successful_request(key_id, json_data["meta"])
            
            return json_data, key_id
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed with key {key_id}: {e}")


# Global instance
_api_manager = None

def get_api_manager() -> StormGlassApiManager:
    """Get the global API manager instance."""
    global _api_manager
    if _api_manager is None:
        _api_manager = StormGlassApiManager()
    return _api_manager


def reset_api_manager():
    """Reset the global API manager (useful for testing)."""
    global _api_manager
    _api_manager = None


if __name__ == "__main__":
    # Test the API manager
    manager = StormGlassApiManager()
    
    print("API Usage Summary:")
    summary = manager.get_usage_summary()
    print(f"Total keys: {summary['total_keys']}")
    print(f"Keys available: {summary['keys_available']}")
    print(f"Total requests today: {summary['total_requests_today']}/{summary['total_quota_today']}")
    
    print("\nKey details:")
    for key_id, details in summary['key_details'].items():
        status = "✓ Available" if details['available'] else "✗ Exhausted"
        print(f"  {key_id}: {details['requests_today']}/{details['daily_quota']} {status}")

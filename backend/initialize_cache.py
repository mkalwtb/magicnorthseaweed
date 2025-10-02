"""
Initialize the forecast cache with basic data.
This ensures there's always something to show users.
"""

import sys
from pathlib import Path

# Add the project root to the path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data_processor import get_processor


def create_fallback_data():
    """Create minimal fallback data when real data isn't available."""
    from datetime import datetime
    
    fallback_html = """
    <div style="text-align: center; padding: 20px;">
        <h3>Surf Forecast</h3>
        <p>Forecast data is currently being updated...</p>
        <p>Please check back in a few minutes for the latest surf conditions.</p>
        <p><small>Last update attempt: {}</small></p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    return {
        "week_overview": fallback_html,
        "spot_tables": {
            "Schev": fallback_html,
            "Noordwijk": fallback_html,
            "ZV": fallback_html,
            "Ijmuiden": fallback_html,
            "Wijk": fallback_html,
            "Camperduin": fallback_html,
            "Texel17": fallback_html,
        },
        "spot_widgets": {
            "Schev": fallback_html,
            "Noordwijk": fallback_html,
            "ZV": fallback_html,
            "Ijmuiden": fallback_html,
            "Wijk": fallback_html,
            "Camperduin": fallback_html,
            "Texel17": fallback_html,
        },
        "generated_at": datetime.now().isoformat(),
        "spots_processed": [],
        "is_fallback": True
    }


def initialize_cache_if_needed():
    """Initialize cache with fallback data if no cache exists."""
    processor = get_processor()
    
    # Check if we have any cached data
    cached_data = processor._load_forecast_data()
    
    if not cached_data:
        print("No cached data found, creating fallback data...")
        fallback_data = create_fallback_data()
        processor._save_forecast_data(fallback_data)
        print("Fallback data created successfully")
        return True
    else:
        print("Cached data already exists")
        return False


if __name__ == "__main__":
    initialize_cache_if_needed()

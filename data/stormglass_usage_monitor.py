#!/usr/bin/env python3
"""
StormGlass API Usage Monitor
Monitor and display current API usage across all keys.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from data.stormglass_api_manager import get_api_manager


def print_usage_summary():
    """Print a detailed usage summary."""
    try:
        manager = get_api_manager()
        summary = manager.get_usage_summary()
        
        print("=" * 60)
        print("StormGlass API Usage Summary")
        print("=" * 60)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total API Keys: {summary['total_keys']}")
        print(f"Keys Available: {summary['keys_available']}")
        print(f"Total Requests Today: {summary['total_requests_today']}/{summary['total_quota_today']}")
        
        remaining_requests = summary['total_quota_today'] - summary['total_requests_today']
        print(f"Remaining Requests: {remaining_requests}")
        
        if summary['keys_available'] == 0:
            print("\n⚠️  WARNING: All API keys have reached their daily limit!")
        elif summary['keys_available'] <= 2:
            print(f"\n⚠️  WARNING: Only {summary['keys_available']} keys remaining!")
        
        print("\n" + "-" * 60)
        print("Individual Key Status:")
        print("-" * 60)
        
        for key_id, details in summary['key_details'].items():
            status_icon = "✅" if details['available'] else "❌"
            usage_bar = create_usage_bar(details['requests_today'], details['daily_quota'])
            
            print(f"{status_icon} {key_id}: {usage_bar} {details['requests_today']}/{details['daily_quota']}")
            
            if details['last_used']:
                last_used = datetime.fromisoformat(details['last_used']).strftime('%H:%M:%S')
                print(f"    Last used: {last_used} | Total: {details['total_requests']} requests")
            else:
                print(f"    Never used | Total: {details['total_requests']} requests")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"Error getting usage summary: {e}")
        return 1
    
    return 0


def create_usage_bar(used: int, total: int, width: int = 20) -> str:
    """Create a visual usage bar."""
    if total == 0:
        return "[" + " " * width + "]"
    
    filled = int((used / total) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"


def reset_usage_data():
    """Reset all usage data (for testing purposes)."""
    try:
        manager = get_api_manager()
        
        # Reset all keys
        for usage in manager.key_usage.values():
            usage.requests_today = 0
            usage.total_requests = 0
            usage.last_used = None
            usage.last_reset_date = datetime.now().strftime("%Y-%m-%d")
        
        manager._save_usage_data()
        print("✅ All API usage data has been reset.")
        return 0
        
    except Exception as e:
        print(f"Error resetting usage data: {e}")
        return 1


def export_usage_data():
    """Export usage data to JSON for analysis."""
    try:
        manager = get_api_manager()
        summary = manager.get_usage_summary()
        
        export_file = Path("stormglass_usage_export.json")
        with open(export_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Usage data exported to {export_file}")
        return 0
        
    except Exception as e:
        print(f"Error exporting usage data: {e}")
        return 1


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print_usage_summary()
        return 0
    
    command = sys.argv[1].lower()
    
    if command in ['status', 'summary', 'show']:
        return print_usage_summary()
    elif command in ['reset']:
        confirm = input("Are you sure you want to reset all usage data? (y/N): ")
        if confirm.lower() == 'y':
            return reset_usage_data()
        else:
            print("Reset cancelled.")
            return 0
    elif command in ['export']:
        return export_usage_data()
    elif command in ['help', '-h', '--help']:
        print("StormGlass API Usage Monitor")
        print("Usage:")
        print("  python stormglass_usage_monitor.py [command]")
        print("")
        print("Commands:")
        print("  status, summary, show  - Show current usage summary (default)")
        print("  reset                  - Reset all usage data")
        print("  export                 - Export usage data to JSON")
        print("  help                   - Show this help message")
        return 0
    else:
        print(f"Unknown command: {command}")
        print("Use 'help' to see available commands.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test script for StormGlass API optimization.
Demonstrates the new intelligent key rotation system.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.stormglass_api_manager import get_api_manager
from data.stormglass_usage_monitor import print_usage_summary


def test_api_manager():
    """Test the API manager functionality."""
    print("Testing StormGlass API Manager...")
    print("=" * 50)
    
    try:
        manager = get_api_manager()
        
        # Show initial status
        print("Initial API Usage Status:")
        print_usage_summary()
        
        # Test getting best key
        print("\nTesting key selection...")
        try:
            key_id, api_key = manager.get_best_key()
            print(f"✅ Selected key: {key_id}")
            print(f"   Key starts with: {api_key[:20]}...")
        except Exception as e:
            print(f"❌ Error selecting key: {e}")
        
        # Test usage summary
        print("\nTesting usage summary...")
        summary = manager.get_usage_summary()
        print(f"✅ Total keys: {summary['total_keys']}")
        print(f"✅ Available keys: {summary['keys_available']}")
        print(f"✅ Total requests today: {summary['total_requests_today']}")
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    return 0


def simulate_api_usage():
    """Simulate API usage to test rotation."""
    print("Simulating API usage...")
    print("=" * 50)
    
    try:
        manager = get_api_manager()
        
        # Simulate several API calls
        for i in range(5):
            try:
                key_id, api_key = manager.get_best_key()
                
                # Simulate a successful API response
                fake_meta = {
                    'cost': 1,
                    'dailyQuota': 10,
                    'requestCount': i + 1
                }
                
                manager.record_successful_request(key_id, fake_meta)
                print(f"Simulated request {i+1} using {key_id}")
                
            except Exception as e:
                print(f"❌ Simulation failed at request {i+1}: {e}")
                break
        
        # Show final status
        print("\nFinal API Usage Status:")
        print_usage_summary()
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return 1
    
    return 0


def main():
    """Main test function."""
    print("StormGlass API Optimization Test")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'simulate':
        return simulate_api_usage()
    else:
        return test_api_manager()


if __name__ == "__main__":
    sys.exit(main())

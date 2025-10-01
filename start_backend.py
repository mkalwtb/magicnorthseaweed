#!/usr/bin/env python
"""
Start the backend data processor and scheduler.
This script runs independently from the Django frontend.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.scheduler import main

if __name__ == "__main__":
    print("Starting Magic North Seaweed Backend...")
    print("This will run the forecast data scheduler every 12 hours.")
    print("Press Ctrl+C to stop.")
    print("-" * 50)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nBackend stopped by user")
    except Exception as e:
        print(f"Backend error: {e}")
        sys.exit(1)

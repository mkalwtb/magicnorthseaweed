#!/usr/bin/env python
"""
Generate a secure Django secret key for production deployment.
"""
import os
import sys
import django
from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    secret_key = get_random_secret_key()
    print(f"Generated Django SECRET_KEY:")
    print(f"SECRET_KEY={secret_key}")
    print(f"\nAdd this to your Railway environment variables.")

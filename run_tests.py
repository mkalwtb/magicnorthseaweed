#!/usr/bin/env python3
"""
Test runner script for Magic North Seaweed.
Provides easy ways to run different test suites.
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print("Make sure pytest is installed: pip install pytest")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Magic North Seaweed Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--django", action="store_true", help="Run Django tests only")
    parser.add_argument("--stormglass", action="store_true", help="Run Stormglass tests only")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--file", help="Run specific test file")
    parser.add_argument("--function", help="Run specific test function")
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["pytest", "tests/"]
    
    # Add options based on arguments
    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])
    elif args.django:
        cmd.extend(["-m", "django"])
    elif args.stormglass:
        cmd.extend(["-m", "stormglass"])
    
    if args.coverage:
        cmd.extend(["--cov=data", "--cov=forecast", "--cov=alert", "--cov-report=html", "--cov-report=term"])
    
    if args.verbose:
        cmd.append("-v")
    
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    if args.file:
        cmd = ["pytest", f"tests/{args.file}"]
    
    if args.function:
        cmd.extend(["-k", args.function])
    
    # Run the tests
    success = run_command(cmd, "Test Suite")
    
    if success:
        print(f"\n🎉 All tests passed!")
        if args.coverage:
            print(f"📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

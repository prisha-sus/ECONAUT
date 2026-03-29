#!/usr/bin/env python3
"""Check if required packages are installed."""

def check_package(package_name):
    try:
        __import__(package_name)
        print(f"{package_name}: OK")
    except ImportError as e:
        print(f"{package_name}: FAILED - {e}")

if __name__ == "__main__":
    check_package("nemoguardrails")
    check_package("memgpt")  # Try memgpt instead of letta
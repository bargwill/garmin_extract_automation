#!/usr/bin/env python3
"""
Garmin Connect Data Extraction Tool - Main Entry Point

This script serves as the main entry point for the Garmin Connect data extraction tool.
It configures the Python path to enable imports from the src/garmin_sync package
and then delegates execution to the CLI module.

Usage:
    python main.py

The script will:
1. Load configuration from environment variables (.env file)
2. Authenticate with Garmin Connect
3. Extract running activities for the specified date range
4. Transform data and extract workout segments
5. Export results to JSON format

Author: Your Name
Date: August 3, 2025
Version: 1.0.0
"""

import sys
import os

# Add src directory to Python path to enable imports
src_path = os.path.join(os.path.dirname(__file__), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from garmin_sync.cli import main

if __name__ == "__main__":
    sys.exit(main())

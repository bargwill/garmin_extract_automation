"""
Package-level configuration for Garmin Extract Automation.

This module provides shared constants and utilities used across the application.
"""

__version__ = "1.0.0"
__author__ = "Garmin Extract Automation"
__description__ = "Automated Garmin Connect data synchronization with training analytics"

# Application constants
APP_NAME = "garmin_extract_automation"
DEFAULT_CSV_FILENAME = "Training-Log.csv"
SUPPORTED_PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]

# Training metric thresholds
ACWR_LOW_THRESHOLD = 0.8
ACWR_HIGH_THRESHOLD = 1.3
MONOTONY_WARNING_THRESHOLD = 3.0

# Date format constants
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

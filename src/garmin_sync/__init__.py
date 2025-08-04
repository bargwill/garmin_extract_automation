"""
Garmin Connect Data Extraction Tool

A Python package for extracting running activity data from Garmin Connect.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .core import Config, authenticate_garmin, fetch_running_activities, transform_activities, export_to_json, run_extraction
from .cli import main

__all__ = [
    "Config",
    "authenticate_garmin", 
    "fetch_running_activities",
    "transform_activities",
    "export_to_json",
    "run_extraction",
    "main"
]

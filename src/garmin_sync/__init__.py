"""
Garmin Connect Data Extraction Package

A modular Python tool for extracting running activity data from Garmin Connect.

Modules:
    core: Main workflow orchestration and configuration
    api_client: Garmin Connect API operations
    data_processor: Data transformation and export utilities
    models: Data models and classes
    cli: Command-line interface

Main Functions:
    run_extraction: Execute the complete data extraction workflow

Author: Your Name
Date: August 5, 2025
Version: 1.1.0
"""

__version__ = "1.1.0"
__author__ = "Your Name"

from .core import Config, run_extraction
from .models import Activity, Segment, ExtractionResult
from .api_client import GarminClient, create_authenticated_client
from .data_processor import DataProcessor, export_to_json

# Legacy imports for backward compatibility (deprecated)
from .core import (
    authenticate_garmin,
    fetch_running_activities,
    transform_activities,
    map_splits_to_segments,
    export_to_json_legacy as export_to_json_old,
)
from .cli import main

__all__ = [
    "Config",
    "authenticate_garmin",
    "fetch_running_activities",
    "transform_activities",
    "export_to_json",
    "run_extraction",
    "main",
]

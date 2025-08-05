"""
Garmin Connect Data Extraction - Core Business Logic

This module contains the main workflow orchestration for the Garmin Connect
data extraction tool. It coordinates between API operations, data processing,
and export functionality using a modular architecture.

Functions:
    run_extraction: Main workflow orchestration function

Classes:
    Config: Configuration management and environment variables

Author: Your Name
Date: August 5, 2025
Version: 1.1.0
"""

import os
import logging
from typing import Optional

from .api_client import create_authenticated_client
from .data_processor import DataProcessor, export_to_json
from .models import ExtractionResult

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass


logger = logging.getLogger(__name__)


class Config:
    """
    Configuration management for Garmin Connect extraction.

    Loads configuration from environment variables with sensible defaults.
    Validates that required credentials are provided.

    Attributes:
        garmin_email (str): Garmin Connect email address (required)
        garmin_password (str): Garmin Connect password (required)
        start_date (str): Data extraction start date in YYYY-MM-DD format
        end_date (str): Data extraction end date in YYYY-MM-DD format
        output_file (str): JSON output file path
        include_metadata (bool): Whether to include extraction metadata in output
        use_detailed_segments (bool): Whether to fetch detailed segment data (requires additional API calls)

    Raises:
        ValueError: If required GARMIN_EMAIL or GARMIN_PASSWORD are not set
    """

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.garmin_email = os.getenv("GARMIN_EMAIL", None)
        self.garmin_password = os.getenv("GARMIN_PASSWORD", None)
        self.start_date = os.getenv("START_DATE", "2025-07-25")
        self.end_date = os.getenv("END_DATE", "2025-07-31")
        self.output_file = os.getenv("OUTPUT_FILE", "running_activities.json")
        self.include_metadata = os.getenv("INCLUDE_METADATA", "true").lower() == "true"
        self.use_detailed_segments = (
            os.getenv("USE_DETAILED_SEGMENTS", "true").lower() == "true"
        )

        # Validate required credentials
        if not self.garmin_email or not self.garmin_password:
            raise ValueError(
                "GARMIN_EMAIL and GARMIN_PASSWORD must be set as environment variables."
            )


def run_extraction(config: Optional[Config] = None) -> int:
    """
    Run the complete data extraction workflow.

    This function orchestrates the entire process:
    1. Authentication with Garmin Connect
    2. Fetching running activities for the specified date range
    3. Transforming raw data into structured models
    4. Exporting results to JSON format

    Args:
        config (Config, optional): Configuration object. If None, creates default config.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    if config is None:
        config = Config()

    try:
        logger.info("Starting Garmin Connect data extraction workflow")

        # Step 1: Authenticate with Garmin Connect
        logger.info("Authenticating with Garmin Connect...")
        # Config validation ensures these are not None
        assert config.garmin_email is not None and config.garmin_password is not None
        garmin_client = create_authenticated_client(
            config.garmin_email, config.garmin_password
        )
        logger.info("Garmin Connect authentication completed successfully")

        # Step 2: Fetch running activities
        logger.info(
            f"Fetching running activities from {config.start_date} to {config.end_date}"
        )
        raw_activities = garmin_client.get_running_activities(
            config.start_date, config.end_date
        )

        # Step 3: Transform data using DataProcessor
        logger.info("Processing and transforming activity data...")
        processor = DataProcessor()

        # Use detailed data if enabled
        if config.use_detailed_segments:
            logger.info("Fetching detailed segment data (this may take longer)...")
            activities = processor.transform_activities(
                raw_activities, garmin_client, use_detailed_data=True
            )
        else:
            logger.info("Using basic segment data...")
            activities = processor.transform_activities(
                raw_activities, use_detailed_data=False
            )

        # Step 4: Create extraction result with metadata
        extraction_result = processor.create_extraction_result(
            activities, config.start_date, config.end_date
        )

        # Mark the extraction as successful
        extraction_result.success = True

        # Step 5: Export to JSON
        logger.info(f"Exporting results to {config.output_file}")
        export_to_json(extraction_result, config.output_file, config.include_metadata)

        logger.info("Data extraction workflow completed successfully")
        return 0

    except Exception as error:
        logger.error(f"Application failed: {error}")
        return 1


# Legacy functions for backward compatibility - these are deprecated
# and will be removed in a future version


def authenticate_garmin(email, password):
    """
    DEPRECATED: Use api_client.create_authenticated_client instead.
    """
    import warnings

    warnings.warn(
        "authenticate_garmin is deprecated. Use api_client.create_authenticated_client instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return create_authenticated_client(email, password)


def fetch_running_activities(garmin_client, start_date, end_date):
    """
    DEPRECATED: Use garmin_client.get_running_activities instead.
    """
    import warnings

    warnings.warn(
        "fetch_running_activities is deprecated. Use garmin_client.get_running_activities instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return garmin_client.get_running_activities(start_date, end_date)


def transform_activities(activities):
    """
    DEPRECATED: Use DataProcessor.transform_activities instead.
    """
    import warnings

    warnings.warn(
        "transform_activities is deprecated. Use DataProcessor.transform_activities instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    processor = DataProcessor()
    return [
        activity.to_dict() for activity in processor.transform_activities(activities)
    ]


def map_splits_to_segments(split_summaries):
    """
    DEPRECATED: Segment creation methods have changed.
    """
    import warnings

    warnings.warn(
        "map_splits_to_segments is deprecated. Segment creation methods have changed.",
        DeprecationWarning,
        stacklevel=2,
    )
    from .models import Segment

    # Return empty list since the old method is no longer available
    logger.warning(
        "map_splits_to_segments called but Segment.from_split_summary no longer exists"
    )
    return []


def export_to_json_legacy(activities_data, output_file):
    """
    DEPRECATED: Use data_processor.export_to_json instead.
    """
    import warnings

    warnings.warn(
        "export_to_json is deprecated. Use data_processor.export_to_json instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    import json

    output_data = {"running_activities": activities_data}
    with open(output_file, "w") as json_file:
        json.dump(output_data, json_file, indent=2)
    print(f"Running activities data exported to {output_file}")

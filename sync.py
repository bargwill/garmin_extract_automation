#!/usr/bin/env python3
"""
Main CLI script for syncing Garmin workout data and generating analytics.

This script fetches workout data from Garmin Connect, calculates training metrics,
exports data to CSV, and optionally sends notifications to Slack.

Usage:
    python sync.py --output Training-Log.csv
    python sync.py --start-date 2024-01-01 --end-date 2024-01-31
    python sync.py --skip-slack --verbose
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import Optional

import pandas as pd

# Import from our modules
from __init__ import DEFAULT_CSV_FILENAME
from analytics import get_workout_metrics, validate_dataframe
from config import default_dates
from garmin_client import fetch_workouts
from slack_notify import notify_slack

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def write_csv(data: pd.DataFrame, path: str) -> None:
    """
    Write DataFrame to CSV file.

    Args:
        data: DataFrame containing workout data
        path: Output file path for CSV

    Raises:
        IOError: If file cannot be written
    """
    try:
        if data is not None and not data.empty:
            data.to_csv(path, index=False)
            logger.info(f"Successfully wrote {len(data)} records to {path}")
        else:
            # Create empty CSV with headers for consistency
            pd.DataFrame(columns=["date", "distance", "duration"]).to_csv(
                path, index=False
            )
            logger.warning(f"No data to write, created empty CSV at {path}")
    except Exception as e:
        logger.error(f"Failed to write CSV to {path}: {e}")
        raise IOError(f"Failed to write CSV: {e}")


def parse_date(date_str: str) -> datetime:
    """
    Parse date string in YYYY-MM-DD format.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        Parsed datetime object

    Raises:
        ValueError: If date string is invalid
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(
            f"Invalid date format '{date_str}'. Use YYYY-MM-DD format."
        ) from e


def parse_args(args: Optional[list] = None) -> argparse.Namespace:
    """
    Parse command line arguments.

    Args:
        args: Optional list of arguments (for testing)

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Sync Garmin workout data and generate analytics",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--output", default=DEFAULT_CSV_FILENAME, help="Output CSV file path"
    )
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date for fetching workouts (YYYY-MM-DD format)",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="End date for fetching workouts (YYYY-MM-DD format)",
    )
    parser.add_argument(
        "--skip-slack", action="store_true", help="Skip Slack notifications"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser.parse_args(args)


def main(args: Optional[list] = None) -> None:
    """
    Main CLI entry point.

    Args:
        args: Optional list of arguments (for testing)

    Raises:
        SystemExit: On configuration or runtime errors
    """
    try:
        parsed_args = parse_args(args)

        # Configure logging level
        if parsed_args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        logger.info("Starting Garmin data sync...")

        # Parse date arguments if provided
        start_date, end_date = None, None
        if parsed_args.start_date:
            start_date = parse_date(parsed_args.start_date)
        if parsed_args.end_date:
            end_date = parse_date(parsed_args.end_date)

        # Use defaults if not specified
        if start_date is None or end_date is None:
            start_date, end_date = default_dates()
            logger.info(
                f"Using default date range: {start_date.date()} to {end_date.date()}"
            )

        # Fetch workout data
        logger.info("Fetching workout data from Garmin...")
        data = fetch_workouts(start_date, end_date)

        if data is not None and not data.empty:
            # Validate data structure
            validate_dataframe(data)

            # Calculate analytics
            logger.info("Calculating workout metrics...")
            metrics = get_workout_metrics(data, return_series=False)

            # Log metrics summary
            acwr_str = (
                f"{metrics.get('acwr'):.3f}"
                if metrics.get("acwr") is not None
                else "N/A"
            )
            monotony_str = (
                f"{metrics.get('monotony'):.3f}"
                if metrics.get("monotony") is not None
                else "N/A"
            )
            logger.info(f"Calculated metrics: ACWR={acwr_str}, Monotony={monotony_str}")

            # Send Slack notification if enabled and configured
            if not parsed_args.skip_slack:
                try:
                    notify_slack(metrics)
                    logger.info("Slack notification sent successfully")
                except Exception as e:
                    logger.warning(f"Slack notification failed: {e}")
        else:
            logger.warning("No workout data retrieved")
            metrics = {"error": "No data available"}

        # Write CSV output
        write_csv(data, parsed_args.output)

        logger.info("Sync completed successfully")

    except KeyboardInterrupt:
        logger.info("Sync interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Garmin Connect API client for fetching workout data.

This module handles authentication and data retrieval from Garmin Connect,
converting raw activity data into pandas DataFrames for analysis.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from garminconnect import Garmin

from config import default_dates, get_garmin_credentials

logger = logging.getLogger(__name__)


def fetch_workouts(
    start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
) -> pd.DataFrame:
    """
    Fetch workouts from Garmin Connect API within the specified date range.

    Args:
        start_date: Start date for fetching workouts. If None, uses default.
        end_date: End date for fetching workouts. If None, uses default.

    Returns:
        DataFrame containing workout data with columns: date, distance, duration, etc.

    Raises:
        RuntimeError: If authentication fails or API request fails.
        ValueError: If date range is invalid.
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = default_dates()
        logger.info(
            f"Using default date range: {start_date.date()} to {end_date.date()}"
        )

    # Validate date range
    if start_date > end_date:
        raise ValueError(
            f"Start date {start_date.date()} must be before end date {end_date.date()}"
        )

    # Get credentials and initialize client
    try:
        user, pwd = get_garmin_credentials()
        api = Garmin(user, pwd)
        logger.debug(f"Initialized Garmin client for user: {user}")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Garmin client: {e}")

    # Authenticate with Garmin Connect
    try:
        api.login()
        logger.info("Successfully authenticated with Garmin Connect")
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise RuntimeError(f"Failed to login to Garmin Connect: {e}")

    # Fetch activities for the date range
    try:
        logger.info(
            f"Fetching activities from {start_date.date()} to {end_date.date()}"
        )
        activities = api.get_activities_by_date(start_date, end_date)
        logger.info(f"Retrieved {len(activities) if activities else 0} activities")
    except Exception as e:
        logger.error(f"Failed to fetch activities: {e}")
        raise RuntimeError(f"Failed to fetch activities from Garmin Connect: {e}")

    # Convert to DataFrame
    if not activities:
        logger.warning("No activities found for the specified date range")
        return pd.DataFrame(columns=["date", "distance", "duration", "activity_type"])

    df = convert_to_dataframe(activities)
    logger.info(f"Converted {len(df)} activities to DataFrame")
    return df


def convert_to_dataframe(activities: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert raw activity JSON data to a pandas DataFrame.

    Args:
        activities: List of activity dictionaries from Garmin Connect API.

    Returns:
        DataFrame with standardized columns for workout analysis.

    Raises:
        ValueError: If activities data is malformed.
    """
    if not activities:
        return pd.DataFrame(columns=["date", "distance", "duration", "activity_type"])

    data = []
    for i, activity in enumerate(activities):
        try:
            # Extract core fields with safe defaults
            activity_data = {
                "date": _parse_garmin_date(
                    activity.get("startTimeLocal", activity.get("startTime"))
                ),
                "distance": _safe_float(activity.get("distance", 0))
                / 1000,  # Convert to km
                "duration": _safe_float(activity.get("duration", 0))
                / 60,  # Convert to minutes
                "activity_type": activity.get("activityType", {}).get(
                    "typeKey", "unknown"
                ),
                "activity_name": activity.get("activityName", ""),
                "calories": _safe_int(activity.get("calories", 0)),
                "avg_speed": _safe_float(activity.get("averageSpeed", 0)),
                "max_speed": _safe_float(activity.get("maxSpeed", 0)),
                "elevation_gain": _safe_float(activity.get("elevationGain", 0)),
                "activity_id": activity.get("activityId", i),
            }
            data.append(activity_data)

        except Exception as e:
            logger.warning(f"Failed to parse activity {i}: {e}")
            # Continue processing other activities
            continue

    if not data:
        raise ValueError("No valid activities could be parsed")

    df = pd.DataFrame(data)

    # Ensure date column is datetime
    df["date"] = pd.to_datetime(df["date"])

    # Sort by date
    df = df.sort_values("date").reset_index(drop=True)

    logger.debug(f"Parsed activities: {df['activity_type'].value_counts().to_dict()}")
    return df


def _parse_garmin_date(date_str: Optional[str]) -> Optional[str]:
    """
    Parse Garmin date string, handling different formats.

    Args:
        date_str: Date string from Garmin API

    Returns:
        Standardized date string or None if parsing fails
    """
    if not date_str:
        return None

    try:
        # Handle ISO format with timezone
        if "T" in date_str:
            return pd.to_datetime(date_str).strftime("%Y-%m-%d")
        else:
            # Try to validate the date string
            pd.to_datetime(date_str)
            return date_str
    except Exception:
        logger.warning(f"Could not parse date: {date_str}")
        return None


def _safe_float(value: Any) -> float:
    """Safely convert value to float, returning 0.0 on failure."""
    try:
        return float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        return 0.0


def _safe_int(value: Any) -> int:
    """Safely convert value to int, returning 0 on failure."""
    try:
        return int(value) if value is not None else 0
    except (ValueError, TypeError):
        return 0

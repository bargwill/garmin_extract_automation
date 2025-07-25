"""
Configuration management for Garmin Connect automation.

This module handles environment variable loading, credential management,
and provides sensible defaults for the application.
"""

import os
from datetime import datetime, timedelta
from typing import Tuple

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_garmin_credentials() -> Tuple[str, str]:
    """
    Retrieve Garmin Connect credentials from environment variables.

    Returns:
        Tuple of (username, password) for Garmin Connect authentication.

    Raises:
        RuntimeError: If either GARMIN_USER or GARMIN_PASS is missing or empty.

    Example:
        >>> user, pwd = get_garmin_credentials()
        >>> api = Garmin(user, pwd)
    """
    user = os.getenv("GARMIN_USER", "").strip()
    pwd = os.getenv("GARMIN_PASS", "").strip()

    if not user or not pwd:
        raise RuntimeError(
            "GARMIN_USER and GARMIN_PASS must be set in the environment. "
            "Check your .env file or environment variables."
        )

    return user, pwd


def get_slack_webhook() -> str:
    """
    Retrieve Slack webhook URL from environment variables.

    Returns:
        Slack webhook URL for sending notifications.

    Raises:
        RuntimeError: If SLACK_WEBHOOK is missing or empty.

    Example:
        >>> webhook_url = get_slack_webhook()
        >>> client = WebhookClient(webhook_url)
    """
    url = os.getenv("SLACK_WEBHOOK", "").strip()

    if not url:
        raise RuntimeError(
            "SLACK_WEBHOOK must be set in the environment. "
            "Check your .env file or environment variables."
        )

    return url


def default_dates(days: int = 30) -> Tuple[datetime, datetime]:
    """
    Generate default start and end dates for workout fetching.

    Args:
        days: Number of days to look back from today (default: 30).

    Returns:
        Tuple of (start_date, end_date) where end_date is now and
        start_date is `days` ago.

    Example:
        >>> start, end = default_dates(7)  # Last 7 days
        >>> start, end = default_dates()   # Last 30 days (default)
    """
    if days <= 0:
        raise ValueError("Days must be a positive integer")

    end = datetime.now()
    start = end - timedelta(days=days)

    return start, end


def is_configured() -> bool:
    """
    Check if the application is properly configured.

    Returns:
        True if all required environment variables are set, False otherwise.

    Example:
        >>> if is_configured():
        ...     print("Ready to sync!")
        ... else:
        ...     print("Please set up your .env file")
    """
    try:
        get_garmin_credentials()
        return True
    except RuntimeError:
        return False


def get_config_summary() -> dict:
    """
    Get a summary of current configuration status.

    Returns:
        Dictionary with configuration status information.

    Example:
        >>> config = get_config_summary()
        >>> print(f"Garmin configured: {config['garmin_configured']}")
    """
    return {
        "garmin_configured": bool(
            os.getenv("GARMIN_USER") and os.getenv("GARMIN_PASS")
        ),
        "slack_configured": bool(os.getenv("SLACK_WEBHOOK")),
        "env_file_exists": os.path.exists(".env"),
    }

"""
Garmin Connect API Client

This module handles all interactions with the Garmin Connect API,
including authentication and data retrieval operations.

Classes:
    GarminClient: Wrapper for Garmin Connect API operations

Functions:
    create_authenticated_client: Factory function for creating authenticated clients

Author: Your Name
Date: August 5, 2025
Version: 1.1.0
"""

import logging
from typing import List, Dict, Any, Optional
import garminconnect


logger = logging.getLogger(__name__)


class GarminClient:
    """
    Wrapper for Garmin Connect API operations.

    Provides a clean interface for authenticating and retrieving data from
    Garmin Connect while handling errors and providing informative logging.

    Attributes:
        client (garminconnect.Garmin): Underlying Garmin Connect client
        username (str): Authenticated username
    """

    def __init__(self, email: str, password: str):
        """
        Initialize and authenticate Garmin Connect client.

        Args:
            email (str): Garmin Connect email address
            password (str): Garmin Connect password

        Raises:
            garminconnect.GarminConnectAuthenticationError: If authentication fails
            Exception: For any other connection errors
        """
        self.client = None
        self.username = None
        self._authenticate(email, password)

    def _authenticate(self, email: str, password: str) -> None:
        """
        Authenticate with Garmin Connect.

        Args:
            email (str): Garmin Connect email address
            password (str): Garmin Connect password

        Raises:
            garminconnect.GarminConnectAuthenticationError: If authentication fails
            Exception: For any other connection errors
        """
        logger.info(f"Attempting to authenticate with Garmin Connect...")
        logger.info(f"Email: {email}")

        try:
            # Initialize Garmin Connect client with credentials
            self.client = garminconnect.Garmin(email, password)

            # Attempt to authenticate
            logger.info("Calling garmin_client.login()...")
            self.client.login()
            self.username = self.client.username
            logger.info(f"Successfully logged in as: {self.username}")

        except garminconnect.GarminConnectAuthenticationError as auth_error:
            logger.error(f"Garmin authentication failed: {auth_error}")
            logger.error("Possible causes:")
            logger.error("1. Incorrect email or password")
            logger.error("2. Two-factor authentication enabled (not supported by API)")
            logger.error("3. Account locked or requires CAPTCHA verification")
            logger.error("4. Try logging into connect.garmin.com first")
            raise

        except Exception as general_error:
            logger.error(f"Unexpected error during login: {general_error}")
            logger.error(f"Error type: {type(general_error).__name__}")
            logger.error(
                "This might be a network issue or Garmin API temporary problem"
            )
            raise

    def get_running_activities(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch running activities for the specified date range.

        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format

        Returns:
            List[Dict]: List of running activity dictionaries from Garmin Connect API

        Raises:
            Exception: If API call fails
        """
        if not self.client:
            raise RuntimeError("Client not authenticated")

        try:
            logger.info(f"Fetching running activities from {start_date} to {end_date}")
            activities = self.client.get_activities_by_date(
                start_date, end_date, "running"
            )
            logger.info(f"Retrieved {len(activities)} running activities")
            return activities

        except Exception as error:
            logger.error(f"Failed to fetch running activities: {error}")
            raise

    def get_activity_details(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information for a specific activity.

        Args:
            activity_id (str): Garmin Connect activity ID

        Returns:
            Dict: Detailed activity data, or None if not found

        Raises:
            Exception: If API call fails
        """
        if not self.client:
            raise RuntimeError("Client not authenticated")

        try:
            logger.debug(f"Fetching details for activity {activity_id}")
            return self.client.get_activity(activity_id)

        except Exception as error:
            logger.warning(
                f"Failed to fetch activity details for {activity_id}: {error}"
            )
            return None

    def get_activity_splits(self, activity_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch chronological lap data for a specific activity.

        This method gets the actual lap-by-lap data in chronological order,
        not the workout step summaries which are grouped by type.

        Args:
            activity_id (str): Garmin Connect activity ID

        Returns:
            List[Dict]: Lap data in chronological order, or None if not available

        Raises:
            Exception: If API call fails
        """
        if not self.client:
            raise RuntimeError("Client not authenticated")

        try:
            logger.debug(f"Fetching lap data for activity {activity_id}")

            # Get activity splits which contains lapDTOs (chronological lap data)
            splits_data = self.client.get_activity_splits(activity_id)

            if splits_data and "lapDTOs" in splits_data:
                lap_dtos = splits_data["lapDTOs"]
                logger.info(f"Retrieved {len(lap_dtos)} laps in chronological order")
                return lap_dtos

            # Fallback: use splitSummaries but warn about ordering issues
            logger.warning("No lapDTOs found, falling back to splitSummaries")
            activity_details = self.get_activity_details(activity_id)
            if activity_details and "splitSummaries" in activity_details:
                logger.warning(
                    "Using splitSummaries - segments may not be in chronological order"
                )
                return activity_details["splitSummaries"]

            return None

        except Exception as error:
            logger.warning(
                f"Failed to fetch activity splits for {activity_id}: {error}"
            )
            return None


def create_authenticated_client(email: str, password: str) -> GarminClient:
    """
    Factory function for creating an authenticated Garmin Connect client.

    Args:
        email (str): Garmin Connect email address
        password (str): Garmin Connect password

    Returns:
        GarminClient: Authenticated client instance

    Raises:
        garminconnect.GarminConnectAuthenticationError: If authentication fails
        Exception: For any other connection errors
    """
    return GarminClient(email, password)

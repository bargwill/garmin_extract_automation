"""
Data Processing and Transformation

This module handles the transformation of raw Garmin Connect data into
structured models and provides utilities for data processing and export.

Classes:
    DataProcessor: Handles data transformation and processing operations

Functions:
    export_to_json: Export processed data to JSON format

Author: Your Name
Date: August 5, 2025
Version: 1.1.0
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import Activity, ExtractionResult


logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Handles transformation of raw Garmin Connect data into structured models.

    This class provides methods for converting raw API responses into
    typed data models and preparing data for export.
    """

    @staticmethod
    def transform_activities(
        raw_activities: List[Dict[str, Any]],
        garmin_client=None,
        use_detailed_data: bool = True,
    ) -> List[Activity]:
        """
        Transform raw Garmin Connect activity data into Activity models.

        Args:
            raw_activities (List[Dict]): Raw activity data from Garmin Connect API
            garmin_client: Optional Garmin client for fetching detailed data
            use_detailed_data (bool): Whether to fetch detailed data for enhanced segments

        Returns:
            List[Activity]: List of transformed Activity objects
        """
        logger.info(f"Transforming {len(raw_activities)} raw activities")

        activities = []
        for raw_activity in raw_activities:
            try:
                # Decide whether to use detailed data
                if (
                    use_detailed_data
                    and garmin_client
                    and raw_activity.get("activityId")
                ):
                    activity_id = str(raw_activity.get("activityId"))
                    logger.debug(f"Fetching detailed data for activity {activity_id}")
                    detailed_data = garmin_client.get_activity_details(activity_id)

                    if detailed_data:
                        # Also try to get chronological lap data
                        lap_data = garmin_client.get_activity_splits(activity_id)
                        if lap_data:
                            # Add lap data to detailed_data for processing
                            detailed_data["_lap_data"] = lap_data
                            logger.debug(
                                f"Retrieved {len(lap_data)} laps for activity {activity_id}"
                            )

                        activity = Activity.from_detailed_garmin_data(
                            raw_activity, detailed_data
                        )
                        logger.debug(
                            f"Created detailed activity: {activity.activity_name}"
                        )
                    else:
                        logger.warning(
                            f"Could not fetch detailed data for {activity_id}, using basic data"
                        )
                        # For basic data without detailed segments, create simple activity
                        activity = Activity(
                            activity_id=str(raw_activity.get("activityId", "")),
                            activity_name=raw_activity.get("activityName", ""),
                            workout_name=raw_activity.get("activityName", ""),
                            date=(
                                raw_activity.get("startTimeLocal", "").split("T")[0]
                                if raw_activity.get("startTimeLocal")
                                else ""
                            ),
                        )
                else:
                    # For basic data without detailed segments, create simple activity
                    activity = Activity(
                        activity_id=str(raw_activity.get("activityId", "")),
                        activity_name=raw_activity.get("activityName", ""),
                        workout_name=raw_activity.get("activityName", ""),
                        date=(
                            raw_activity.get("startTimeLocal", "").split("T")[0]
                            if raw_activity.get("startTimeLocal")
                            else ""
                        ),
                    )

                activities.append(activity)
                logger.debug(
                    f"Transformed activity: {activity.workout_name} on {activity.date}"
                )

            except Exception as error:
                logger.warning(f"Failed to transform activity: {error}")
                logger.debug(f"Raw activity data: {raw_activity}")
                continue

        logger.info(f"Successfully transformed {len(activities)} activities")
        activity_dates = [activity.date for activity in activities]
        logger.info(f"Activities found on dates: {activity_dates}")

        return activities

    @staticmethod
    def create_extraction_result(
        activities: List[Activity], start_date: str, end_date: str
    ) -> ExtractionResult:
        """
        Create an ExtractionResult containing processed activities and metadata.

        Args:
            activities (List[Activity]): Processed activity objects
            start_date (str): Extraction start date
            end_date (str): Extraction end date

        Returns:
            ExtractionResult: Complete extraction result with metadata
        """
        current_time = datetime.now().isoformat()
        date_range = {"start_date": start_date, "end_date": end_date}

        return ExtractionResult(
            activities=activities, extraction_date=current_time, date_range=date_range
        )

    @staticmethod
    def enrich_activity_data(
        activity: Activity, additional_data: Dict[str, Any]
    ) -> Activity:
        """
        Enrich an activity with additional data from detailed API calls.

        This method can be used to add more detailed information to activities
        by making additional API calls for specific activity details.

        Args:
            activity (Activity): Base activity object
            additional_data (Dict): Additional data to merge

        Returns:
            Activity: Enriched activity object
        """
        # Create a copy of the activity with additional data
        activity_dict = activity.to_dict()

        # Merge additional data (this is where you'd add new fields)
        for key, value in additional_data.items():
            if hasattr(activity, key) and value is not None:
                setattr(activity, key, value)

        logger.debug(f"Enriched activity {activity.workout_name} with additional data")
        return activity

    @staticmethod
    def filter_activities_by_criteria(
        activities: List[Activity],
        min_distance: Optional[float] = None,
        min_duration: Optional[int] = None,
        activity_types: Optional[List[str]] = None,
    ) -> List[Activity]:
        """
        Filter activities based on specified criteria.

        Note: This is a legacy method that may not work with current streamlined Activity model.
        Consider updating based on your specific filtering needs.

        Args:
            activities (List[Activity]): Activities to filter
            min_distance (float, optional): Minimum distance in miles (not implemented in current model)
            min_duration (int, optional): Minimum duration in seconds (not implemented in current model)
            activity_types (List[str], optional): Allowed activity types/names

        Returns:
            List[Activity]: Filtered activities
        """
        filtered = activities.copy()

        # Note: Current Activity model doesn't have total_distance_mi or total_time_sec
        # These would need to be computed from segments or added to the model

        if activity_types is not None:
            activity_types_lower = [t.lower() for t in activity_types]
            filtered = [
                a
                for a in filtered
                if any(t in a.activity_name.lower() for t in activity_types_lower)
            ]
            logger.info(
                f"Filtered by activity types {activity_types}: {len(filtered)} activities"
            )

        return filtered


def export_to_json(
    extraction_result: ExtractionResult, output_file: str, include_metadata: bool = True
) -> None:
    """
    Export extraction results to JSON file.

    Args:
        extraction_result (ExtractionResult): Complete extraction results
        output_file (str): Path to output JSON file
        include_metadata (bool): Whether to include extraction metadata

    Raises:
        IOError: If file cannot be written
    """
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if include_metadata:
            output_data = extraction_result.to_dict()
        else:
            # Legacy format - just activities
            activities = extraction_result.activities or []
            output_data = {
                "running_activities": [activity.to_dict() for activity in activities]
            }

        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(output_data, json_file, indent=2, ensure_ascii=False)

        activities_count = (
            len(extraction_result.activities) if extraction_result.activities else 0
        )
        logger.info(f"Exported {activities_count} activities to {output_file}")

    except Exception as error:
        logger.error(f"Failed to export data to {output_file}: {error}")
        raise


def export_to_csv(extraction_result: ExtractionResult, output_file: str) -> None:
    """
    Export extraction results to CSV file.

    Note: This function uses pandas and exports a simplified view of activities.
    The current Activity model has been streamlined, so this creates a basic export.

    Args:
        extraction_result (ExtractionResult): Complete extraction results
        output_file (str): Path to output CSV file

    Raises:
        ImportError: If pandas is not available
        IOError: If file cannot be written
    """
    try:
        import pandas as pd

        # Convert activities to flat dictionaries for CSV
        activities = extraction_result.activities or []
        rows = []
        for activity in activities:
            # Basic activity data from current streamlined model
            row = {
                "date": activity.date,
                "activity_name": activity.activity_name,
                "workout_name": activity.workout_name,
                "activity_id": activity.activity_id,
                "num_segments": len(activity.segments or []),
            }

            # If segments exist, aggregate some basic metrics
            if activity.segments:
                total_duration = sum(
                    s.duration_seconds for s in activity.segments if s.duration_seconds
                )
                total_distance = sum(
                    s.distance_miles for s in activity.segments if s.distance_miles
                )
                total_calories = sum(
                    s.calories for s in activity.segments if s.calories
                )

                row.update(
                    {
                        "total_duration_seconds": total_duration,
                        "total_distance_miles": total_distance,
                        "total_calories": total_calories,
                    }
                )

            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False)

        activities_count = len(activities)
        logger.info(f"Exported {activities_count} activities to CSV: {output_file}")

    except ImportError:
        logger.error(
            "pandas is required for CSV export. Install with: pip install pandas"
        )
        raise
    except Exception as error:
        logger.error(f"Failed to export data to CSV {output_file}: {error}")
        raise

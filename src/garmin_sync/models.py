"""
Data Models for Garmin Connect Data Extraction

This module defines the core data models for representing Garmin Connect
activities and segments in a structured, type-safe format.

Classes:
    Segment: Represents a workout segment with essential metrics  
    Activity: Represents a complete running activity with segments
    ExtractionResult: Container for complete extraction results with metadata

Author: Your Name
Date: August 5, 2025
Version: 1.1.0
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Segment:
    """
    Represents a workout segment with essential performance metrics.

    Focused on the most important training data: timing, distance, pace,
    heart rate, cadence, and energy expenditure. Designed for lightweight
    analysis and AI-powered insights.

    Attributes:
        segment_index: Segment sequence number (1, 2, 3...)
        type: Segment type (warmup, active, recovery, cooldown)
        duration_seconds: Duration in seconds
        duration_formatted: Human-readable duration (MM:SS)
        distance_miles: Distance covered in miles
        avg_pace_per_mile: Average pace (MM:SS per mile)
        avg_hr: Average heart rate (BPM)
        avg_cadence: Average running cadence (steps per minute)
        calories: Calories burned during segment
    """

    # Essential identification and timing
    segment_index: Optional[int] = None
    type: str = ""
    duration_seconds: int = 0
    duration_formatted: str = ""

    # Distance and pace metrics
    distance_miles: float = 0.0
    avg_pace_per_mile: str = ""

    # Physiological metrics
    avg_hr: Optional[int] = None
    avg_cadence: Optional[int] = None

    # Energy metrics
    calories: Optional[int] = None

    # Legacy fields (maintained for compatibility)
    distance_meters: float = 0.0
    avg_pace_per_km: str = ""
    max_hr: Optional[int] = None
    avg_speed_mph: float = 0.0
    avg_speed_kph: float = 0.0
    max_speed_mph: float = 0.0
    max_speed_kph: float = 0.0
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_lap_data(cls, lap_data: Dict[str, Any], index: Optional[int] = None):
        """Create a Segment from chronological lap data (lapDTOs)."""
        segment_type = lap_data.get("intensityType", "unknown").lower()
        duration_seconds = lap_data.get("duration", 0)
        distance_meters = lap_data.get("distance", 0.0)
        distance_miles = distance_meters * 0.000621371 if distance_meters else 0.0

        # Format duration
        duration_seconds = int(duration_seconds) if duration_seconds else 0
        minutes, seconds = divmod(duration_seconds, 60)
        duration_formatted = f"{minutes}:{seconds:02d}"

        # Calculate pace
        avg_pace_per_mile = ""
        if distance_miles > 0:
            pace_seconds_per_mile = duration_seconds / distance_miles
            pace_minutes = int(pace_seconds_per_mile // 60)
            pace_secs = int(pace_seconds_per_mile % 60)
            avg_pace_per_mile = f"{pace_minutes}:{pace_secs:02d}"

        return cls(
            segment_index=index,
            type=segment_type,
            duration_seconds=duration_seconds,
            duration_formatted=duration_formatted,
            distance_miles=distance_miles,
            avg_pace_per_mile=avg_pace_per_mile,
            avg_hr=lap_data.get("averageHR"),
            avg_cadence=lap_data.get("averageRunCadence"),
            calories=lap_data.get("calories"),
        )

    def to_dict(self):
        """Convert to dictionary with only essential 8 fields."""
        return {
            "segment_index": self.segment_index,
            "type": self.type,
            "duration_seconds": self.duration_seconds,
            "distance_miles": self.distance_miles,
            "avg_pace_per_mile": self.avg_pace_per_mile,
            "avg_hr": self.avg_hr,
            "avg_cadence": self.avg_cadence,
            "calories": self.calories,
        }


@dataclass
class Activity:
    """
    Represents a complete Garmin activity with metadata and segment data.

    Combines high-level activity information with detailed segment performance
    data. Segment data is sourced from lapDTOs for chronological accuracy,
    providing the proper sequence of intervals as they occurred during the workout.

    Attributes:
        activity_id: Unique Garmin activity identifier (as string)
        activity_name: User-defined activity name
        segments: List of chronologically ordered segments (from lap data)
        workout_name: Workout name (typically same as activity_name)
        date: Activity date in YYYY-MM-DD format
    """

    activity_id: str = ""
    activity_name: str = ""
    segments: Optional[List[Segment]] = None
    workout_name: str = ""
    date: str = ""

    def __post_init__(self):
        if self.segments is None:
            self.segments = []

    @classmethod
    def from_detailed_garmin_data(
        cls, raw_data: Dict[str, Any], detailed_data: Dict[str, Any]
    ):
        """Create Activity from detailed Garmin data using lap data for proper segment order."""
        activity = cls(
            activity_id=str(raw_data.get("activityId", "")),
            activity_name=raw_data.get("activityName", ""),
            workout_name=raw_data.get("activityName", ""),
            date=(
                raw_data.get("startTimeLocal", "").split("T")[0]
                if raw_data.get("startTimeLocal")
                else ""
            ),
        )

        # Process lap data for chronological segments
        if detailed_data and "_lap_data" in detailed_data:
            lap_data = detailed_data["_lap_data"]
            if activity.segments is None:
                activity.segments = []
            for i, lap in enumerate(lap_data, 1):
                segment = Segment.from_lap_data(lap, index=i)
                activity.segments.append(segment)

        return activity

    def to_dict(self):
        """Convert to dictionary for compatibility - lightweight version with only essential fields."""
        return {
            "activity_id": self.activity_id,
            "activity_name": self.activity_name,
            "workout_name": self.workout_name,
            "date": self.date,
            "segments": [s.to_dict() for s in self.segments] if self.segments else [],
        }


@dataclass
class ExtractionResult:
    """
    Container for activity extraction results with metadata.

    Provides a standardized format for extraction outcomes, including
    success status, extracted activities, error information, and
    extraction metadata for tracking and debugging.

    Attributes:
        success: Whether the extraction completed successfully
        activity: Single activity result (for single activity extraction)
        activities: List of activities (for bulk extraction)
        error_message: Error details if extraction failed
        extraction_date: When the extraction was performed
        date_range: Date range for bulk extractions
    """

    success: bool = False
    activity: Optional[Activity] = None
    activities: Optional[List[Activity]] = None
    error_message: Optional[str] = None
    extraction_date: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None

    def to_dict(self):
        """Convert to dictionary for export."""
        return {
            "success": self.success,
            "activities": [activity.to_dict() for activity in (self.activities or [])],
            "extraction_date": self.extraction_date,
            "date_range": self.date_range,
            "error_message": self.error_message,
        }

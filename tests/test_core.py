"""
Test suite for Garmin Connect Data Extraction - Core Module

Tests the core business logic functions including data transformation,
model creation, and configuration management for the updated streamlined API.

Author: Your Name
Date: August 5, 2025
Version: 1.1.0
"""

import sys
import os

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from garmin_sync.models import Segment, Activity, ExtractionResult
from garmin_sync.core import Config


def test_segment_from_lap_data():
    """Test segment creation from lap data."""
    sample_lap_data = {
        "startTimeGMT": "2025-08-01T10:00:00.000",
        "duration": 30.0,
        "distance": 400.0,  # meters
        "averageSpeed": 3.0,  # m/s
        "averageHR": 150,
        "averageRunCadence": 180,
        "calories": 15,
    }

    segment = Segment.from_lap_data(sample_lap_data, index=1)

    assert segment.segment_index == 1
    assert segment.duration_seconds == 30
    assert abs(segment.distance_miles - 0.249) < 0.001  # More flexible precision check
    assert segment.avg_hr == 150
    assert segment.avg_cadence == 180
    assert segment.calories == 15


def test_activity_from_detailed_data():
    """Test activity creation from detailed Garmin data."""
    raw_data = {
        "activityId": 12345,
        "activityName": "Morning Run",
        "startTimeLocal": "2025-08-01T06:00:00.000",
    }

    detailed_data = {
        "_lap_data": [
            {
                "startTimeGMT": "2025-08-01T10:00:00.000",
                "duration": 30.0,
                "distance": 400.0,
                "averageSpeed": 3.0,
                "averageHR": 150,
                "averageRunCadence": 180,
                "calories": 15,
            }
        ]
    }

    activity = Activity.from_detailed_garmin_data(raw_data, detailed_data)

    assert activity.activity_id == "12345"
    assert activity.activity_name == "Morning Run"
    assert activity.date == "2025-08-01"
    assert activity.segments is not None
    assert len(activity.segments) == 1
    assert activity.segments[0].segment_index == 1


def test_extraction_result_to_dict():
    """Test ExtractionResult serialization."""
    activity = Activity(
        activity_id="12345", activity_name="Test Run", date="2025-08-01"
    )

    result = ExtractionResult(
        success=True,
        activities=[activity],
        extraction_date="2025-08-01T12:00:00.000",
        date_range={"start_date": "2025-08-01", "end_date": "2025-08-01"},
    )

    result_dict = result.to_dict()

    assert result_dict["success"] is True
    assert len(result_dict["activities"]) == 1
    assert result_dict["activities"][0]["activity_id"] == "12345"
    assert result_dict["extraction_date"] == "2025-08-01T12:00:00.000"


def test_config_initialization():
    """Test Config class initialization."""
    # This will use environment variables or defaults
    # Note: This test assumes GARMIN_EMAIL and GARMIN_PASSWORD are set
    try:
        config = Config()
        assert hasattr(config, "garmin_email")
        assert hasattr(config, "garmin_password")
        assert hasattr(config, "start_date")
        assert hasattr(config, "end_date")
        assert hasattr(config, "output_file")
        assert isinstance(config.include_metadata, bool)
        assert isinstance(config.use_detailed_segments, bool)
    except ValueError:
        # This is expected if credentials aren't set in the environment
        print("Skipping config test - credentials not available")


# Streamlined segment data structure tests
def test_segment_to_dict_streamlined():
    """Test segment serialization with streamlined 8-field output."""
    segment = Segment(
        segment_index=1,
        type="active",
        duration_seconds=30,
        distance_miles=0.25,
        avg_pace_per_mile="6:00",
        avg_hr=150,
        avg_cadence=180,
        calories=15,
    )

    segment_dict = segment.to_dict()

    # Should only have 8 essential fields
    expected_fields = {
        "segment_index",
        "type",
        "duration_seconds",
        "distance_miles",
        "avg_pace_per_mile",
        "avg_hr",
        "avg_cadence",
        "calories",
    }

    assert set(segment_dict.keys()) == expected_fields
    assert segment_dict["segment_index"] == 1
    assert segment_dict["type"] == "active"
    assert segment_dict["avg_hr"] == 150


def test_activity_to_dict():
    """Test Activity to_dict method includes segments."""
    segment = Segment(
        segment_index=1,
        type="active",
        duration_seconds=30,
        distance_miles=0.25,
        avg_pace_per_mile="6:00",
        avg_hr=150,
        avg_cadence=180,
        calories=15,
    )

    activity = Activity(
        activity_id="12345",
        activity_name="Test Run",
        date="2025-08-01",
        segments=[segment],
    )

    activity_dict = activity.to_dict()

    assert activity_dict["activity_id"] == "12345"
    assert activity_dict["activity_name"] == "Test Run"
    assert len(activity_dict["segments"]) == 1
    assert activity_dict["segments"][0]["segment_index"] == 1


def test_empty_segments_handling():
    """Test handling of activities with no segments."""
    activity = Activity(
        activity_id="12345", activity_name="Test Run", date="2025-08-01"
    )

    activity_dict = activity.to_dict()

    assert activity_dict["activity_id"] == "12345"
    assert activity_dict["segments"] == []

"""
Test suite for the refactored Garmin Connect Data Extraction modules

Tests the new modular architecture including models, data processing,
and API client functionality.

Author: Your Name
Date: August 5, 2025
Version: 1.1.0
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from garmin_sync.models import Segment, Activity, ExtractionResult
from garmin_sync.data_processor import DataProcessor
from garmin_sync.core import Config


class TestSegmentModel(unittest.TestCase):
    """Test cases for the Segment data model."""

    def test_segment_from_lap_data(self):
        """Test creating a segment from lap data."""
        sample_lap = {
            "intensityType": "ACTIVE",
            "duration": 300,
            "averageSpeed": 3.5,
            "distance": 1000,
            "averageHR": 150,
            "averageRunCadence": 180,
            "calories": 50,
        }

        segment = Segment.from_lap_data(sample_lap, index=1)

        self.assertEqual(segment.type, "active")
        self.assertEqual(segment.duration_seconds, 300)
        self.assertEqual(segment.segment_index, 1)
        self.assertEqual(segment.avg_hr, 150)
        self.assertEqual(segment.avg_cadence, 180)
        self.assertEqual(segment.calories, 50)

    def test_segment_type_normalization(self):
        """Test segment type normalization with current API."""
        test_cases = [
            ("ACTIVE", "active"),
            ("WARMUP", "warmup"),
            ("COOLDOWN", "cooldown"),
            ("REST", "rest"),
        ]

        for input_type, expected_type in test_cases:
            lap_data = {"intensityType": input_type, "duration": 30, "averageSpeed": 3.0, "distance": 100}
            segment = Segment.from_lap_data(lap_data, index=1)
            self.assertEqual(segment.type, expected_type)

    def test_segment_to_dict(self):
        """Test segment dictionary conversion."""
        segment = Segment(
            segment_index=1,
            type="active",
            duration_seconds=300,
            distance_miles=0.25,
            avg_pace_per_mile="5:00",
            avg_hr=150,
            avg_cadence=180,
            calories=50,
        )

        result = segment.to_dict()

        # Check that the result contains exactly the 8 essential fields
        expected_fields = {
            "segment_index", "type", "duration_seconds", "distance_miles", 
            "avg_pace_per_mile", "avg_hr", "avg_cadence", "calories"
        }
        self.assertEqual(set(result.keys()), expected_fields)
        self.assertEqual(result["type"], "active")
        self.assertEqual(result["duration_seconds"], 300)
        self.assertEqual(result["avg_hr"], 150)


class TestActivityModel(unittest.TestCase):
    """Test cases for the Activity data model."""

    def test_activity_from_detailed_garmin_data(self):
        """Test creating an activity from detailed Garmin Connect data."""
        raw_data = {
            "activityId": 12345,
            "activityName": "Morning Run",
            "startTimeLocal": "2025-08-05T07:30:00.000",
        }
        
        detailed_data = {
            "_lap_data": [
                {
                    "intensityType": "WARMUP",
                    "duration": 300,
                    "distance": 500,
                    "averageSpeed": 2.5,
                    "averageHR": 135,
                    "averageRunCadence": 170,
                    "calories": 25,
                },
                {
                    "intensityType": "ACTIVE", 
                    "duration": 1200,
                    "distance": 3000,
                    "averageSpeed": 3.5,
                    "averageHR": 155,
                    "averageRunCadence": 180,
                    "calories": 100,
                },
            ]
        }

        activity = Activity.from_detailed_garmin_data(raw_data, detailed_data)

        self.assertEqual(activity.date, "2025-08-05")
        self.assertEqual(activity.workout_name, "Morning Run")
        self.assertEqual(activity.activity_id, "12345")
        self.assertIsNotNone(activity.segments)
        if activity.segments is not None:
            self.assertEqual(len(activity.segments), 2)
            self.assertEqual(activity.segments[0].type, "warmup")
            self.assertEqual(activity.segments[1].type, "active")

    def test_activity_to_dict(self):
        """Test activity dictionary conversion."""
        segment = Segment(
            segment_index=1,
            type="active", 
            duration_seconds=300,
            distance_miles=0.25,
            avg_pace_per_mile="5:00",
            avg_hr=150,
            avg_cadence=180,
            calories=50
        )
        activity = Activity(
            activity_id="12345",
            activity_name="Test Run",
            workout_name="Test Run",
            date="2025-08-05",
            segments=[segment],
        )

        result = activity.to_dict()

        self.assertEqual(result["date"], "2025-08-05")
        self.assertEqual(result["workout_name"], "Test Run")
        self.assertEqual(result["activity_id"], "12345")
        self.assertEqual(len(result["segments"]), 1)
        self.assertEqual(result["segments"][0]["type"], "active")


class TestDataProcessor(unittest.TestCase):
    """Test cases for the DataProcessor class."""

    def test_transform_activities_basic(self):
        """Test transforming raw activities with basic data only."""
        raw_activities = [
            {
                "activityId": 1,
                "activityName": "Run 1",
                "startTimeLocal": "2025-08-05T07:00:00.000",
            },
            {
                "activityId": 2,
                "activityName": "Run 2", 
                "startTimeLocal": "2025-08-06T07:00:00.000",
            },
        ]

        processor = DataProcessor()
        activities = processor.transform_activities(raw_activities, use_detailed_data=False)

        self.assertEqual(len(activities), 2)
        self.assertEqual(activities[0].workout_name, "Run 1")
        self.assertEqual(activities[1].workout_name, "Run 2")
        self.assertEqual(activities[0].date, "2025-08-05")
        self.assertEqual(activities[1].date, "2025-08-06")

    def test_create_extraction_result(self):
        """Test creating extraction result with metadata."""
        activities = [
            Activity(
                activity_id="123",
                activity_name="Test Run",
                workout_name="Test Run",
                date="2025-08-05",
            )
        ]

        processor = DataProcessor()
        result = processor.create_extraction_result(
            activities, "2025-08-01", "2025-08-07"
        )

        self.assertIsNotNone(result.activities)
        if result.activities:
            self.assertEqual(len(result.activities), 1)
        self.assertIsNotNone(result.date_range)
        if result.date_range:
            self.assertEqual(result.date_range["start_date"], "2025-08-01")
            self.assertEqual(result.date_range["end_date"], "2025-08-07")
        self.assertIsInstance(result.extraction_date, str)

    def test_filter_activities_by_criteria(self):
        """Test filtering activities by activity name patterns."""
        activities = [
            Activity(
                activity_id="1",
                activity_name="Short Run",
                workout_name="Short Run",
                date="2025-08-05",
            ),
            Activity(
                activity_id="2", 
                activity_name="Long Run",
                workout_name="Long Run",
                date="2025-08-06",
            ),
            Activity(
                activity_id="3",
                activity_name="Tempo Run",
                workout_name="Tempo Run", 
                date="2025-08-07",
            ),
        ]

        processor = DataProcessor()

        # Test activity type filter
        filtered = processor.filter_activities_by_criteria(
            activities, activity_types=["tempo"]
        )
        self.assertEqual(len(filtered), 1)  # Only Tempo Run
        self.assertEqual(filtered[0].activity_name, "Tempo Run")


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""

    @patch.dict(
        os.environ,
        {
            "GARMIN_EMAIL": "test@example.com",
            "GARMIN_PASSWORD": "testpass",
            "START_DATE": "2025-08-01",
            "END_DATE": "2025-08-07",
            "OUTPUT_FILE": "test_output.json",
        },
    )
    def test_config_from_environment(self):
        """Test config loading from environment variables."""
        config = Config()

        self.assertEqual(config.garmin_email, "test@example.com")
        self.assertEqual(config.garmin_password, "testpass")
        self.assertEqual(config.start_date, "2025-08-01")
        self.assertEqual(config.end_date, "2025-08-07")
        self.assertEqual(config.output_file, "test_output.json")

    @patch.dict(os.environ, {}, clear=True)
    def test_config_missing_credentials(self):
        """Test config validation with missing credentials."""
        with self.assertRaises(ValueError) as context:
            Config()

        self.assertIn("GARMIN_EMAIL and GARMIN_PASSWORD", str(context.exception))


if __name__ == "__main__":
    unittest.main()

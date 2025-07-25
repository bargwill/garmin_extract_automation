"""
Unit tests for Garmin client functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd

from garmin_client import (
    fetch_workouts,
    convert_to_dataframe,
    _parse_garmin_date,
    _safe_float,
    _safe_int
)


@patch('garmin_client.get_garmin_credentials')
@patch('garmin_client.Garmin')
def test_fetch_workouts_success(mock_garmin_class, mock_get_creds):
    """Test successful workout fetching."""
    # Setup mocks
    mock_get_creds.return_value = ("user", "pass")
    mock_api = MagicMock()
    mock_garmin_class.return_value = mock_api
    mock_api.get_activities_by_date.return_value = [
        {
            "startTimeLocal": "2024-01-01T10:00:00",
            "distance": 5000,  # meters
            "duration": 1800,  # seconds
            "activityType": {"typeKey": "running"},
            "activityName": "Morning Run",
            "calories": 300,
            "activityId": 123
        }
    ]
    
    # Test
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)
    result = fetch_workouts(start, end)
    
    # Verify
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["distance"] == 5.0  # Converted to km
    assert result.iloc[0]["duration"] == 30.0  # Converted to minutes
    assert result.iloc[0]["activity_type"] == "running"


@patch('garmin_client.get_garmin_credentials')
@patch('garmin_client.Garmin')
def test_fetch_workouts_auth_failure(mock_garmin_class, mock_get_creds):
    """Test workout fetching with authentication failure."""
    mock_get_creds.return_value = ("user", "pass")
    mock_api = MagicMock()
    mock_garmin_class.return_value = mock_api
    mock_api.login.side_effect = Exception("Auth failed")
    
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)
    
    with pytest.raises(RuntimeError, match="Failed to login to Garmin Connect"):
        fetch_workouts(start, end)


@patch('garmin_client.get_garmin_credentials')
@patch('garmin_client.Garmin')
def test_fetch_workouts_api_failure(mock_garmin_class, mock_get_creds):
    """Test workout fetching with API failure."""
    mock_get_creds.return_value = ("user", "pass")
    mock_api = MagicMock()
    mock_garmin_class.return_value = mock_api
    mock_api.get_activities_by_date.side_effect = Exception("API failed")
    
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)
    
    with pytest.raises(RuntimeError, match="Failed to fetch activities"):
        fetch_workouts(start, end)


@patch('garmin_client.get_garmin_credentials')
@patch('garmin_client.Garmin')
def test_fetch_workouts_no_activities(mock_garmin_class, mock_get_creds):
    """Test workout fetching with no activities."""
    mock_get_creds.return_value = ("user", "pass")
    mock_api = MagicMock()
    mock_garmin_class.return_value = mock_api
    mock_api.get_activities_by_date.return_value = []
    
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)
    result = fetch_workouts(start, end)
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
    assert "date" in result.columns


def test_fetch_workouts_invalid_date_range():
    """Test workout fetching with invalid date range."""
    start = datetime(2024, 1, 2)
    end = datetime(2024, 1, 1)  # End before start
    
    with pytest.raises(ValueError, match="Start date .* must be before end date"):
        fetch_workouts(start, end)


def test_convert_to_dataframe_success():
    """Test successful activity conversion to DataFrame."""
    activities = [
        {
            "startTimeLocal": "2024-01-01T10:00:00",
            "distance": 5000,
            "duration": 1800,
            "activityType": {"typeKey": "running"},
            "activityName": "Morning Run",
            "calories": 300,
            "activityId": 123
        },
        {
            "startTimeLocal": "2024-01-02T08:00:00", 
            "distance": 3000,
            "duration": 1200,
            "activityType": {"typeKey": "cycling"},
            "activityName": "Evening Ride",
            "calories": 200,
            "activityId": 124
        }
    ]
    
    result = convert_to_dataframe(activities)
    
    assert len(result) == 2
    assert result.iloc[0]["distance"] == 5.0  # Converted to km
    assert result.iloc[1]["distance"] == 3.0
    assert result.iloc[0]["activity_type"] == "running"
    assert result.iloc[1]["activity_type"] == "cycling"


def test_convert_to_dataframe_empty():
    """Test activity conversion with empty list."""
    result = convert_to_dataframe([])
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
    assert "date" in result.columns


def test_convert_to_dataframe_malformed():
    """Test activity conversion with malformed data."""
    activities = [
        {"startTimeLocal": "2024-01-01T10:00:00"},  # Missing most fields
        {"distance": 5000},  # Missing date
    ]
    
    result = convert_to_dataframe(activities)
    
    # Should handle malformed data gracefully
    assert isinstance(result, pd.DataFrame)
    # May have 0, 1, or 2 rows depending on how much can be parsed


def test_parse_garmin_date_iso():
    """Test Garmin date parsing with ISO format."""
    result = _parse_garmin_date("2024-01-01T10:00:00")
    assert result == "2024-01-01"


def test_parse_garmin_date_simple():
    """Test Garmin date parsing with simple format."""
    result = _parse_garmin_date("2024-01-01")
    assert result == "2024-01-01"


def test_parse_garmin_date_invalid():
    """Test Garmin date parsing with invalid format."""
    result = _parse_garmin_date("invalid")
    assert result is None


def test_parse_garmin_date_none():
    """Test Garmin date parsing with None input."""
    result = _parse_garmin_date(None)
    assert result is None


def test_safe_float():
    """Test safe float conversion."""
    assert _safe_float("5.5") == 5.5
    assert _safe_float(10) == 10.0
    assert _safe_float(None) == 0.0
    assert _safe_float("invalid") == 0.0


def test_safe_int():
    """Test safe integer conversion."""
    assert _safe_int("5") == 5
    assert _safe_int(10.7) == 10
    assert _safe_int(None) == 0
    assert _safe_int("invalid") == 0

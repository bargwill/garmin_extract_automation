"""
Integration tests for the sync module.

Tests CLI parsing, end-to-end workflow, and CSV output generation.
"""

import os
import tempfile
from unittest.mock import patch, MagicMock
import pytest
import pandas as pd

from sync import parse_args, main


def test_parse_args_defaults():
    """Test that parse_args returns correct defaults."""
    args = parse_args([])
    assert args.output == "Training-Log.csv"
    assert args.start_date is None
    assert args.end_date is None
    assert args.skip_slack is False
    assert args.verbose is False


def test_parse_args_with_arguments():
    """Test parse_args with custom arguments."""
    args = parse_args(
        [
            "--output",
            "custom.csv",
            "--start-date",
            "2024-01-01",
            "--end-date",
            "2024-01-31",
            "--skip-slack",
            "--verbose",
        ]
    )
    assert args.output == "custom.csv"
    assert args.start_date == "2024-01-01"
    assert args.end_date == "2024-01-31"
    assert args.skip_slack is True
    assert args.verbose is True


@patch("sync.fetch_workouts")
@patch("sync.notify_slack")
def test_main_creates_csv(mock_slack, mock_fetch, tmp_path):
    """Test that main() creates CSV output file."""
    # Setup mock data
    mock_data = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "distance": [5.0, 3.2],
            "duration": [30, 20],
            "activity_type": ["running", "cycling"],
        }
    )
    mock_fetch.return_value = mock_data
    mock_slack.return_value = True

    # Setup output path
    output_path = tmp_path / "test_output.csv"

    # Set environment variables
    with patch.dict(
        os.environ,
        {
            "GARMIN_USER": "test_user",
            "GARMIN_PASS": "test_pass",
            "SLACK_WEBHOOK": "https://hooks.slack.com/test",
        },
    ):
        # Run main with test arguments
        main(["--output", str(output_path), "--skip-slack"])

    # Verify CSV was created
    assert output_path.exists()

    # Verify CSV content
    result_df = pd.read_csv(output_path)
    assert len(result_df) == 2
    assert "date" in result_df.columns
    assert "distance" in result_df.columns


@patch("sync.fetch_workouts")
def test_main_handles_empty_data(mock_fetch, tmp_path):
    """Test that main() handles empty data gracefully."""
    mock_fetch.return_value = pd.DataFrame()

    output_path = tmp_path / "empty_output.csv"

    with patch.dict(
        os.environ, {"GARMIN_USER": "test_user", "GARMIN_PASS": "test_pass"}
    ):
        main(["--output", str(output_path), "--skip-slack"])

    # Should still create CSV file
    assert output_path.exists()


@patch("sync.fetch_workouts")
def test_main_handles_fetch_error(mock_fetch, tmp_path):
    """Test that main() handles fetch errors gracefully."""
    mock_fetch.side_effect = RuntimeError("API Error")

    output_path = tmp_path / "error_output.csv"

    with patch.dict(
        os.environ, {"GARMIN_USER": "test_user", "GARMIN_PASS": "test_pass"}
    ):
        with pytest.raises(SystemExit):
            main(["--output", str(output_path), "--skip-slack"])


def test_parse_date_invalid():
    """Test date parsing with invalid format."""
    from sync import parse_date

    with pytest.raises(ValueError, match="Invalid date format"):
        parse_date("invalid-date")


def test_parse_date_valid():
    """Test date parsing with valid format."""
    from sync import parse_date

    result = parse_date("2024-01-15")
    assert result.year == 2024
    assert result.month == 1
    assert result.day == 15

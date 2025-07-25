"""
Unit tests for configuration management.
"""

import os
import pytest
from unittest.mock import patch

from config import (
    get_garmin_credentials,
    get_slack_webhook, 
    default_dates,
    is_configured,
    get_config_summary
)


def test_get_garmin_credentials_success():
    """Test successful credential retrieval."""
    with patch.dict(os.environ, {
        'GARMIN_USER': 'test@example.com',
        'GARMIN_PASS': 'password123'
    }):
        user, pwd = get_garmin_credentials()
        assert user == 'test@example.com'
        assert pwd == 'password123'


def test_get_garmin_credentials_missing():
    """Test credential retrieval with missing values."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="GARMIN_USER and GARMIN_PASS must be set"):
            get_garmin_credentials()


def test_get_slack_webhook_success():
    """Test successful webhook retrieval."""
    webhook_url = "https://hooks.slack.com/test"
    with patch.dict(os.environ, {'SLACK_WEBHOOK': webhook_url}):
        result = get_slack_webhook()
        assert result == webhook_url


def test_get_slack_webhook_missing():
    """Test webhook retrieval with missing value."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="SLACK_WEBHOOK must be set"):
            get_slack_webhook()


def test_default_dates():
    """Test default date generation."""
    start, end = default_dates(7)
    
    # Should be 7 days apart
    diff = end - start
    assert diff.days == 7
    
    # End should be more recent than start
    assert end > start


def test_default_dates_invalid():
    """Test default dates with invalid input."""
    with pytest.raises(ValueError, match="Days must be a positive integer"):
        default_dates(-1)


def test_is_configured_true():
    """Test configuration check when properly configured."""
    with patch.dict(os.environ, {
        'GARMIN_USER': 'test@example.com',
        'GARMIN_PASS': 'password123'
    }):
        assert is_configured() is True


def test_is_configured_false():
    """Test configuration check when not configured."""
    with patch.dict(os.environ, {}, clear=True):
        assert is_configured() is False


def test_get_config_summary():
    """Test configuration summary."""
    with patch.dict(os.environ, {
        'GARMIN_USER': 'test@example.com',
        'GARMIN_PASS': 'password123',
        'SLACK_WEBHOOK': 'https://hooks.slack.com/test'
    }):
        summary = get_config_summary()
        assert summary['garmin_configured'] is True
        assert summary['slack_configured'] is True
        assert 'env_file_exists' in summary

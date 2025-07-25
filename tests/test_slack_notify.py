"""
Unit tests for Slack notification functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

from slack_notify import (
    send_slack_message,
    format_metrics_message,
    create_metrics_blocks,
    notify_slack
)


@patch('slack_notify.get_slack_webhook')
@patch('slack_notify.WebhookClient')
def test_send_slack_message_success(mock_webhook_client, mock_get_webhook):
    """Test successful Slack message sending."""
    # Setup mocks
    mock_get_webhook.return_value = "https://hooks.slack.com/test"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_webhook_instance = MagicMock()
    mock_webhook_instance.send.return_value = mock_response
    mock_webhook_client.return_value = mock_webhook_instance
    
    # Test message sending
    result = send_slack_message("Test message")
    
    assert result is True
    mock_webhook_instance.send.assert_called_once_with(text="Test message")


@patch('slack_notify.get_slack_webhook')
def test_send_slack_message_config_error(mock_get_webhook):
    """Test Slack message sending with configuration error."""
    mock_get_webhook.side_effect = RuntimeError("SLACK_WEBHOOK not set")
    
    with pytest.raises(RuntimeError, match="SLACK_WEBHOOK not set"):
        send_slack_message("Test message")


def test_format_metrics_message_success():
    """Test metrics message formatting with valid data."""
    metrics = {
        "acwr": 1.2,
        "monotony": 2.1,
        "total_distance": 25.5,
        "avg_daily_distance": 5.1,
        "days_with_data": 5
    }
    
    message = format_metrics_message(metrics)
    
    assert "🏃 *Workout Analytics Summary*" in message
    assert "1.200" in message  # ACWR formatted to 3 decimals
    assert "2.100" in message  # Monotony formatted to 3 decimals
    assert "25.5 km" in message  # Total distance
    assert "5.1 km" in message   # Avg daily distance
    assert "5" in message        # Days with data


def test_format_metrics_message_with_error():
    """Test metrics message formatting with error."""
    metrics = {"error": "API connection failed"}
    
    message = format_metrics_message(metrics)
    
    assert "⚠️ Workout Sync Error: API connection failed" == message


def test_format_metrics_message_training_status():
    """Test training status interpretation in message."""
    # Low ACWR
    metrics = {"acwr": 0.7, "monotony": 2.0, "total_distance": 10, "days_with_data": 7}
    message = format_metrics_message(metrics)
    assert "🔵 *Training Status:* Low training load" in message
    
    # High ACWR
    metrics = {"acwr": 1.5, "monotony": 2.0, "total_distance": 10, "days_with_data": 7}
    message = format_metrics_message(metrics)
    assert "🔴 *Training Status:* High training load" in message
    
    # Optimal ACWR
    metrics = {"acwr": 1.0, "monotony": 2.0, "total_distance": 10, "days_with_data": 7}
    message = format_metrics_message(metrics)
    assert "🟢 *Training Status:* Optimal training load" in message


def test_create_metrics_blocks_success():
    """Test Block Kit block creation with valid metrics."""
    metrics = {
        "acwr": 1.2,
        "monotony": 2.1,
        "total_distance": 25.5,
        "days_with_data": 5
    }
    
    blocks = create_metrics_blocks(metrics)
    
    assert len(blocks) == 2  # Header + section
    assert blocks[0]["type"] == "header"
    assert blocks[1]["type"] == "section"
    assert "fields" in blocks[1]


def test_create_metrics_blocks_with_error():
    """Test Block Kit block creation with error."""
    metrics = {"error": "Test error"}
    
    blocks = create_metrics_blocks(metrics)
    
    assert len(blocks) == 1
    assert blocks[0]["type"] == "section"
    assert "Test error" in blocks[0]["text"]["text"]


@patch('slack_notify.send_slack_message')
def test_notify_slack_success(mock_send):
    """Test successful Slack notification."""
    mock_send.return_value = True
    
    metrics = {"acwr": 1.2, "monotony": 2.1}
    result = notify_slack(metrics)
    
    assert result is True
    mock_send.assert_called_once()


@patch('slack_notify.send_slack_message')
def test_notify_slack_config_error(mock_send):
    """Test Slack notification with configuration error."""
    mock_send.side_effect = RuntimeError("SLACK_WEBHOOK not set")
    
    metrics = {"acwr": 1.2, "monotony": 2.1}
    result = notify_slack(metrics)
    
    assert result is False

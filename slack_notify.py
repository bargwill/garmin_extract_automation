"""
Slack notification handler for workout analytics.

This module sends formatted workout summaries and analytics to Slack
via incoming webhooks, with robust error handling and logging.
"""

import logging
from typing import Any, Dict, Optional

from slack_sdk.errors import SlackApiError
from slack_sdk.webhook import WebhookClient

from __init__ import ACWR_HIGH_THRESHOLD, ACWR_LOW_THRESHOLD
from config import get_slack_webhook

logger = logging.getLogger(__name__)


def send_slack_message(text: str, blocks: Optional[list] = None) -> bool:
    """
    Send a message to Slack using the configured webhook URL.

    Args:
        text: The message text to send to Slack.
        blocks: Optional Slack Block Kit blocks for rich formatting.

    Returns:
        True if message was sent successfully, False otherwise.

    Raises:
        RuntimeError: If SLACK_WEBHOOK is not configured.

    Example:
        >>> success = send_slack_message("Hello from Garmin automation!")
        >>> if success:
        ...     print("Message sent!")
    """
    try:
        webhook_url = get_slack_webhook()
    except RuntimeError as e:
        logger.error(f"Slack not configured: {e}")
        raise

    webhook = WebhookClient(webhook_url)

    try:
        payload = {"text": text}
        if blocks:
            payload["blocks"] = blocks

        response = webhook.send(**payload)

        if response.status_code == 200:
            logger.info("Slack message sent successfully")
            return True
        else:
            logger.error(f"Slack API error {response.status_code}: {response.body}")
            return False

    except SlackApiError as e:
        logger.error(f"Slack API error: {e.response['error']}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending Slack message: {e}")
        return False


def format_metrics_message(metrics: Dict[str, Any]) -> str:
    """
    Format workout metrics into a readable Slack message.

    Args:
        metrics: Dictionary containing workout metrics.

    Returns:
        Formatted message string for Slack.
    """
    if metrics.get("error"):
        return f"⚠️ Workout Sync Error: {metrics['error']}"

    # Format numbers safely
    def format_number(value: Any, decimals: int = 2) -> str:
        try:
            if value is None:
                return "N/A"
            return f"{float(value):.{decimals}f}"
        except (ValueError, TypeError):
            return "N/A"

    message_parts = [
        "🏃 *Workout Analytics Summary*",
        "",
        f"📊 *Training Load Metrics:*",
        f"• ACWR (Acute:Chronic): {format_number(metrics.get('acwr'), 3)}",
        f"• Monotony Index: {format_number(metrics.get('monotony'), 3)}",
        f"• ACWR (Sum-based): {format_number(metrics.get('acwr_sum_based'), 3)}",
        "",
        f"📈 *Activity Summary:*",
        f"• Total Distance: {format_number(metrics.get('total_distance'), 1)} km",
        f"• Avg Daily Distance: {format_number(metrics.get('avg_daily_distance'), 1)} km",
        f"• Days with Data: {metrics.get('days_with_data', 0)}",
    ]

    # Add interpretation if ACWR is available
    acwr = metrics.get("acwr")
    if acwr is not None:
        try:
            acwr_val = float(acwr)
            if acwr_val < ACWR_LOW_THRESHOLD:
                message_parts.append("")
                message_parts.append(
                    "🔵 *Training Status:* Low training load - consider increasing"
                )
            elif acwr_val > ACWR_HIGH_THRESHOLD:
                message_parts.append("")
                message_parts.append(
                    "🔴 *Training Status:* High training load - consider recovery"
                )
            else:
                message_parts.append("")
                message_parts.append("🟢 *Training Status:* Optimal training load")
        except (ValueError, TypeError):
            pass

    return "\n".join(message_parts)


def create_metrics_blocks(metrics: Dict[str, Any]) -> list:
    """
    Create Slack Block Kit blocks for rich metric formatting.

    Args:
        metrics: Dictionary containing workout metrics.

    Returns:
        List of Slack Block Kit blocks.
    """
    if metrics.get("error"):
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *Workout Sync Error*\n{metrics['error']}",
                },
            }
        ]

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🏃 Workout Analytics Summary"},
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*ACWR:*\n{metrics.get('acwr', 'N/A'):.3f}"
                    if metrics.get("acwr")
                    else "*ACWR:*\nN/A",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Monotony:*\n{metrics.get('monotony', 'N/A'):.3f}"
                    if metrics.get("monotony")
                    else "*Monotony:*\nN/A",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Total Distance:*\n{metrics.get('total_distance', 0):.1f} km",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Days Active:*\n{metrics.get('days_with_data', 0)}",
                },
            ],
        },
    ]

    return blocks


def notify_slack(metrics: Dict[str, Any], use_blocks: bool = True) -> bool:
    """
    Send workout metrics notification to Slack.

    Args:
        metrics: Dictionary containing calculated workout metrics.
        use_blocks: Whether to use rich Block Kit formatting.

    Returns:
        True if notification was sent successfully, False otherwise.

    Example:
        >>> metrics = {"acwr": 1.2, "monotony": 2.1, "total_distance": 45.5}
        >>> success = notify_slack(metrics)
    """
    try:
        if use_blocks:
            blocks = create_metrics_blocks(metrics)
            text = "Workout Analytics Summary"  # Fallback text
            return send_slack_message(text, blocks)
        else:
            message = format_metrics_message(metrics)
            return send_slack_message(message)

    except RuntimeError:
        # Slack not configured - this is expected in some environments
        logger.info("Slack notifications not configured, skipping...")
        return False
    except Exception as e:
        logger.warning(f"Slack notification failed: {e}")
        return False

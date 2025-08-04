"""
Test suite for Garmin Connect Data Extraction - Core Module

Tests the core business logic functions including segments mapping,
data transformation, and configuration management.

Author: Your Name
Date: August 3, 2025
Version: 1.0.0
"""

import sys
import os

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from garmin_sync.core import map_splits_to_segments


def test_map_splits_to_segments_basic():
    """Test basic split mapping functionality."""
    sample = [{
        "splitType": "INTERVAL_ACTIVE",
        "duration": 30,
        "averageSpeed": 3.0
    }]
    result = map_splits_to_segments(sample)
    expected = [{
        "type": "active",
        "duration_sec": 30,
        "avg_pace_sec_per_mi": round(1609.344/3.0, 2)
    }]
    assert result == expected


def test_map_splits_to_segments_warmup():
    """Test warmup split mapping."""
    sample = [{
        "splitType": "INTERVAL_WARMUP",
        "duration": 600,
        "averageSpeed": 2.4189999103546143
    }]
    result = map_splits_to_segments(sample)
    expected = [{
        "type": "warmup",
        "duration_sec": 600,
        "avg_pace_sec_per_mi": 665.29
    }]
    assert result == expected


def test_map_splits_to_segments_recovery():
    """Test recovery (walk) split mapping."""
    sample = [{
        "splitType": "INTERVAL_WALK",
        "duration": 120,
        "averageSpeed": 1.5
    }]
    result = map_splits_to_segments(sample)
    expected = [{
        "type": "recovery",
        "duration_sec": 120,
        "avg_pace_sec_per_mi": round(1609.344/1.5, 2)
    }]
    assert result == expected


def test_map_splits_to_segments_rwd_prefix():
    """Test RWD prefix stripping."""
    sample = [{
        "splitType": "RWD_COOLDOWN",
        "duration": 300,
        "averageSpeed": 2.0
    }]
    result = map_splits_to_segments(sample)
    expected = [{
        "type": "cooldown",
        "duration_sec": 300,
        "avg_pace_sec_per_mi": round(1609.344/2.0, 2)
    }]
    assert result == expected


def test_map_splits_to_segments_zero_speed():
    """Test handling of zero or missing speed."""
    sample = [{
        "splitType": "INTERVAL_REST",
        "duration": 60,
        "averageSpeed": 0
    }]
    result = map_splits_to_segments(sample)
    expected = [{
        "type": "rest",
        "duration_sec": 60,
        "avg_pace_sec_per_mi": 0
    }]
    assert result == expected


def test_map_splits_to_segments_multiple():
    """Test mapping multiple splits."""
    sample = [
        {
            "splitType": "INTERVAL_WARMUP",
            "duration": 300,
            "averageSpeed": 2.5
        },
        {
            "splitType": "INTERVAL_ACTIVE",
            "duration": 60,
            "averageSpeed": 4.0
        },
        {
            "splitType": "INTERVAL_WALK",
            "duration": 90,
            "averageSpeed": 1.2
        }
    ]
    result = map_splits_to_segments(sample)
    expected = [
        {
            "type": "warmup",
            "duration_sec": 300,
            "avg_pace_sec_per_mi": round(1609.344/2.5, 2)
        },
        {
            "type": "active",
            "duration_sec": 60,
            "avg_pace_sec_per_mi": round(1609.344/4.0, 2)
        },
        {
            "type": "recovery",
            "duration_sec": 90,
            "avg_pace_sec_per_mi": round(1609.344/1.2, 2)
        }
    ]
    assert result == expected

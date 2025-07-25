"""
Unit tests for analytics functions.

Tests ACWR, monotony calculations, and data validation with known inputs.
"""

import pytest
import pandas as pd
import numpy as np

from analytics import (
    acwr, 
    monotony, 
    get_workout_metrics, 
    validate_dataframe,
    create_sample_data
)


def test_acwr_basic_calculation():
    """Test ACWR calculation with known values."""
    # Create synthetic data with predictable ACWR
    dates = pd.date_range("2024-01-01", periods=35, freq="D")
    distances = [5.0] * 35  # Consistent 5km daily
    df = pd.DataFrame({"date": dates, "distance": distances})
    
    # With consistent training, ACWR should be close to 1.0
    result = acwr(df, acute_days=7, chronic_days=28)
    assert result is not None
    assert 0.8 <= result <= 1.2  # Should be close to 1.0 for consistent training


def test_acwr_different_methods():
    """Test ACWR with different chronic calculation methods."""
    dates = pd.date_range("2024-01-01", periods=35, freq="D")
    distances = [5.0] * 35
    df = pd.DataFrame({"date": dates, "distance": distances})
    
    acwr_mean = acwr(df, chronic_method='mean')
    acwr_sum = acwr(df, chronic_method='sum')
    
    assert acwr_mean is not None
    assert acwr_sum is not None
    assert acwr_mean != acwr_sum  # Different methods should give different results


def test_acwr_insufficient_data():
    """Test ACWR with insufficient data."""
    df = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "distance": [5.0, 3.0]
    })
    
    with pytest.raises(ValueError, match="Insufficient data"):
        acwr(df)


def test_acwr_full_series():
    """Test ACWR returning full time series."""
    dates = pd.date_range("2024-01-01", periods=35, freq="D")
    distances = [5.0] * 35
    df = pd.DataFrame({"date": dates, "distance": distances})
    
    result = acwr(df, latest_only=False)
    assert isinstance(result, pd.Series)
    assert len(result) > 1


def test_monotony_basic_calculation():
    """Test monotony calculation with known values."""
    # High monotony: very consistent training
    dates = pd.date_range("2024-01-01", periods=14, freq="D")
    distances = [5.0] * 14  # Very consistent
    df = pd.DataFrame({"date": dates, "distance": distances})
    
    result = monotony(df, window=7)
    assert result is not None
    assert result > 5  # High monotony for consistent training


def test_monotony_varied_training():
    """Test monotony with varied training loads."""
    dates = pd.date_range("2024-01-01", periods=14, freq="D")
    distances = [1, 10, 2, 8, 3, 9, 1, 5, 15, 2, 7, 3, 12, 1]  # Highly varied
    df = pd.DataFrame({"date": dates, "distance": distances})
    
    result = monotony(df, window=7)
    assert result is not None
    assert result < 5  # Lower monotony for varied training


def test_monotony_with_daily_aggregation():
    """Test monotony with daily aggregation enabled."""
    # Multiple entries per day
    dates = ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"] * 4
    distances = [2.5, 2.5, 3.0, 2.0] * 4  # Two 2.5km runs per day
    df = pd.DataFrame({"date": dates, "distance": distances})
    
    result = monotony(df, aggregate_daily=True)
    assert result is not None


def test_validate_dataframe_valid():
    """Test dataframe validation with valid data."""
    df = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "distance": [5.0, 3.0]
    })
    
    # Should not raise any exception
    validate_dataframe(df)


def test_validate_dataframe_missing_columns():
    """Test dataframe validation with missing columns."""
    df = pd.DataFrame({"date": ["2024-01-01"], "wrong_col": [5.0]})
    
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_dataframe(df)


def test_validate_dataframe_negative_distance():
    """Test dataframe validation with negative distances."""
    df = pd.DataFrame({
        "date": ["2024-01-01"],
        "distance": [-5.0]
    })
    
    with pytest.raises(ValueError, match="Distance values must be non-negative"):
        validate_dataframe(df)


def test_validate_dataframe_empty():
    """Test dataframe validation with empty dataframe."""
    df = pd.DataFrame({"date": [], "distance": []})
    
    with pytest.raises(ValueError, match="DataFrame is empty"):
        validate_dataframe(df)


def test_get_workout_metrics_complete():
    """Test get_workout_metrics with complete data."""
    dates = pd.date_range("2024-01-01", periods=35, freq="D")
    distances = [5.0] * 35
    df = pd.DataFrame({"date": dates, "distance": distances})
    
    metrics = get_workout_metrics(df)
    
    assert "acwr" in metrics
    assert "monotony" in metrics
    assert "acwr_sum_based" in metrics
    assert "total_distance" in metrics
    assert "avg_daily_distance" in metrics
    assert "days_with_data" in metrics
    
    assert metrics["total_distance"] == 175.0  # 35 * 5.0
    assert metrics["avg_daily_distance"] == 5.0
    assert metrics["days_with_data"] == 35


def test_get_workout_metrics_insufficient_data():
    """Test get_workout_metrics with insufficient data."""
    df = pd.DataFrame({
        "date": ["2024-01-01"],
        "distance": [5.0]
    })
    
    metrics = get_workout_metrics(df)
    
    assert metrics["acwr"] is None
    assert metrics["monotony"] is None
    assert "error" in metrics


def test_get_workout_metrics_as_series():
    """Test get_workout_metrics returning pandas Series."""
    dates = pd.date_range("2024-01-01", periods=35, freq="D")
    distances = [5.0] * 35
    df = pd.DataFrame({"date": dates, "distance": distances})
    
    metrics = get_workout_metrics(df, return_series=True)
    
    assert isinstance(metrics, pd.Series)
    assert "acwr" in metrics.index


def test_create_sample_data():
    """Test sample data generation."""
    df = create_sample_data(days=30)
    
    assert len(df) == 30
    assert "date" in df.columns
    assert "distance" in df.columns
    assert df["distance"].min() >= 0  # Non-negative distances
    assert df["date"].dtype == "datetime64[ns]"


def test_create_sample_data_custom():
    """Test sample data generation with custom parameters."""
    df = create_sample_data(days=10, start_date="2023-06-01")
    
    assert len(df) == 10
    assert df["date"].min() == pd.Timestamp("2023-06-01")


def test_acwr_invalid_method():
    """Test ACWR with invalid chronic method."""
    df = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "distance": [5.0, 3.0]
    })
    
    with pytest.raises(ValueError, match="chronic_method must be either"):
        acwr(df, chronic_method='invalid')
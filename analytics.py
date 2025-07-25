# Computes ACWR and monotony metrics.
"""
Training analytics module for calculating workout metrics.

This module provides functions to calculate key training load metrics including:
- ACWR (Acute:Chronic Workload Ratio) 
- Monotony index
- General workout statistics

The metrics help monitor training load and injury risk patterns.
"""

import pandas as pd
from typing import Optional, Union

# Constants for default metric calculations
DEFAULT_ACUTE_DAYS = 7
DEFAULT_CHRONIC_DAYS = 28
DEFAULT_MONOTONY_WINDOW = 7
MIN_DATA_POINTS = 7  # Minimum data points for meaningful calculations

def acwr(df: pd.DataFrame, acute_days: int = DEFAULT_ACUTE_DAYS, chronic_days: int = DEFAULT_CHRONIC_DAYS, 
         chronic_method: str = 'mean', latest_only: bool = True, 
         min_periods: Optional[int] = None) -> Union[float, pd.Series, None]:
    """
    Calculate Acute Chronic Workload Ratio (ACWR) from workout data.
    
    ACWR compares acute (short-term) vs chronic (long-term) training loads.
    Formula: acute_workload (7-day sum) / chronic_workload (28-day mean or sum)
    
    Args:
        df (pd.DataFrame): DataFrame containing workout data with 'date' and 'distance' columns.
        acute_days (int): Number of days for acute workload calculation (default: 7).
        chronic_days (int): Number of days for chronic workload calculation (default: 28).
        chronic_method (str): Method for chronic calculation - 'mean' or 'sum' (default: 'mean').
        latest_only (bool): If True, return only the latest value; if False, return full series.
        min_periods (int): Minimum number of observations required for rolling calculation.
    
    Returns:
        Union[float, pd.Series, None]: ACWR value(s) or None if insufficient data.
        
    Raises:
        ValueError: If chronic_method is not 'mean' or 'sum'.
        ValueError: If insufficient data for calculation.
    """
    if chronic_method not in ['mean', 'sum']:
        raise ValueError("chronic_method must be either 'mean' or 'sum'")
    
    if len(df) == 0:
        return None
        
    # Ensure we have enough data for chronic calculation
    if min_periods is None:
        min_periods = max(MIN_DATA_POINTS, acute_days)  # Use sensible minimum
    
    if len(df) < min_periods:
        raise ValueError(f"Insufficient data: need at least {min_periods} days, got {len(df)}")
    
    # Prepare time series
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    series = df_copy.set_index('date')['distance'].sort_index()
    
    # Calculate rolling workloads
    acute_workload = series.rolling(window=acute_days, min_periods=min_periods).sum()
    
    if chronic_method == 'mean':
        chronic_workload = series.rolling(window=chronic_days, min_periods=min_periods).mean()
    else:  # sum
        chronic_workload = series.rolling(window=chronic_days, min_periods=min_periods).sum()
    
    # Calculate ACWR, handling divide-by-zero
    with pd.option_context('mode.use_inf_as_na', True):
        acwr_series = acute_workload / chronic_workload
    
    # Remove infinite and NaN values
    acwr_series = acwr_series.replace([float('inf'), -float('inf')], pd.NA).dropna()
    
    if acwr_series.empty:
        return None
    
    return acwr_series.iloc[-1] if latest_only else acwr_series

def monotony(df: pd.DataFrame, window: int = DEFAULT_MONOTONY_WINDOW, latest_only: bool = True, 
             min_periods: Optional[int] = None, 
             aggregate_daily: bool = True) -> Union[float, pd.Series, None]:
    """
    Calculate monotony of workload from workout data.
    
    Monotony measures training variety - lower values indicate more varied training.
    Formula: rolling_mean_workload / rolling_std_workload over specified window
    
    Args:
        df (pd.DataFrame): DataFrame containing workout data with 'date' and 'distance' columns.
        window (int): Number of days for rolling calculation (default: 7 for weekly).
        latest_only (bool): If True, return only the latest value; if False, return full series.
        min_periods (int): Minimum number of observations required for rolling calculation.
        aggregate_daily (bool): If True, aggregate multiple entries per day to daily totals.
    
    Returns:
        Union[float, pd.Series, None]: Monotony value(s) or None if insufficient data.
        
    Raises:
        ValueError: If insufficient data for calculation.
    """
    if len(df) == 0:
        return None
        
    if min_periods is None:
        min_periods = max(MIN_DATA_POINTS, window)
        
    if len(df) < min_periods:
        raise ValueError(f"Insufficient data: need at least {min_periods} days, got {len(df)}")
    
    # Prepare time series
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    
    if aggregate_daily:
        # Aggregate multiple entries per day to daily totals
        daily_data = df_copy.groupby('date')['distance'].sum().reset_index()
        series = daily_data.set_index('date')['distance'].sort_index()
    else:
        series = df_copy.set_index('date')['distance'].sort_index()
    
    # Calculate rolling mean and standard deviation
    rolling_mean = series.rolling(window=window, min_periods=min_periods).mean()
    rolling_std = series.rolling(window=window, min_periods=min_periods).std()
    
    # Calculate monotony, handling divide-by-zero
    with pd.option_context('mode.use_inf_as_na', True):
        monotony_series = rolling_mean / rolling_std
    
    # Remove infinite and NaN values
    monotony_series = monotony_series.replace([float('inf'), -float('inf')], pd.NA).dropna()
    
    if monotony_series.empty:
        return None
    
    return monotony_series.iloc[-1] if latest_only else monotony_series

def get_workout_metrics(df: pd.DataFrame, return_series: bool = False) -> Union[dict, pd.Series]:
    """
    Get comprehensive workout metrics from the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing workout data with 'date' and 'distance' columns.
        return_series (bool): If True, return pandas Series; if False, return dict.
    
    Returns:
        Union[dict, pd.Series]: Dictionary or Series containing ACWR and monotony values.
        
    Raises:
        ValueError: If insufficient data for calculations.
    """
    try:
        metrics = {
            "acwr": acwr(df),
            "monotony": monotony(df),
            "acwr_sum_based": acwr(df, chronic_method='sum'),
            "total_distance": df['distance'].sum() if len(df) > 0 else 0,
            "avg_daily_distance": df['distance'].mean() if len(df) > 0 else 0,
            "days_with_data": len(df)
        }
        
        if return_series:
            return pd.Series(metrics)
        return metrics
        
    except ValueError as e:
        # Return metrics with None values if insufficient data
        metrics = {
            "acwr": None,
            "monotony": None, 
            "acwr_sum_based": None,
            "total_distance": df['distance'].sum() if len(df) > 0 else 0,
            "avg_daily_distance": df['distance'].mean() if len(df) > 0 else 0,
            "days_with_data": len(df),
            "error": str(e)
        }
        
        if return_series:
            return pd.Series(metrics)
        return metrics


def validate_dataframe(df: pd.DataFrame) -> None:
    """
    Validate that the DataFrame has the required columns and data types.
    
    Args:
        df (pd.DataFrame): DataFrame to validate.
        
    Raises:
        ValueError: If DataFrame is invalid.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    required_columns = ['date', 'distance']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    if len(df) == 0:
        raise ValueError("DataFrame is empty")
    
    # Check for non-negative distances
    if (df['distance'] < 0).any():
        raise ValueError("Distance values must be non-negative")


def create_sample_data(days: int = 60, start_date: str = "2024-01-01") -> pd.DataFrame:
    """
    Create sample workout data for testing purposes.
    
    Args:
        days (int): Number of days of data to generate.
        start_date (str): Start date in YYYY-MM-DD format.
        
    Returns:
        pd.DataFrame: Sample workout data with date and distance columns.
    """
    import numpy as np
    
    dates = pd.date_range(start=start_date, periods=days, freq='D')
    
    # Generate realistic workout distances with some variation
    np.random.seed(42)  # For reproducible results
    base_distance = 5.0
    distances = np.random.normal(base_distance, 2.0, days)
    distances = np.maximum(distances, 0)  # Ensure non-negative
    
    # Add some rest days (zero distance)
    rest_days = np.random.choice(days, size=days//7, replace=False)
    distances[rest_days] = 0
    
    return pd.DataFrame({
        'date': dates,
        'distance': distances
    })
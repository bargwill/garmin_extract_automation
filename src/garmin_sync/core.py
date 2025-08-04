"""
Garmin Connect Data Extraction - Core Business Logic

This module contains all the business logic for authenticating with Garmin Connect,
fetching activity data, transforming it, and exporting to JSON format. It includes
support for detailed workout segments extracted from split summaries.

Functions:
    authenticate_garmin: Establish connection to Garmin Connect API
    fetch_running_activities: Retrieve running activities from specified date range
    transform_activities: Convert raw API data to standardized format with segments
    map_splits_to_segments: Convert splitSummaries to structured segment data
    export_to_json: Export processed data to JSON file
    run_extraction: Orchestrate complete extraction workflow

Classes:
    Config: Manage configuration and environment variables

Author: Your Name
Date: August 3, 2025
Version: 1.0.0
"""

import json
import os
import garminconnect

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass

# Conversion constants
METERS_TO_MILES = 1609.344


class Config:
    """
    Configuration management for Garmin Connect extraction.
    
    Loads configuration from environment variables with sensible defaults.
    Validates that required credentials are provided.
    
    Attributes:
        garmin_email (str): Garmin Connect email address (required)
        garmin_password (str): Garmin Connect password (required)
        start_date (str): Data extraction start date in YYYY-MM-DD format
        end_date (str): Data extraction end date in YYYY-MM-DD format  
        output_file (str): JSON output file path
        
    Raises:
        ValueError: If required GARMIN_EMAIL or GARMIN_PASSWORD are not set
    """
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.garmin_email = os.getenv('GARMIN_EMAIL', None)
        self.garmin_password = os.getenv('GARMIN_PASSWORD', None)
        self.start_date = os.getenv('START_DATE', "2025-07-25")
        self.end_date = os.getenv('END_DATE', "2025-07-31")
        self.output_file = os.getenv('OUTPUT_FILE', "running_activities.json")
        
        # Validate required credentials
        if not self.garmin_email or not self.garmin_password:
            raise ValueError("GARMIN_EMAIL and GARMIN_PASSWORD must be set as environment variables.")


def authenticate_garmin(email, password):
    """
    Authenticate with Garmin Connect.
    
    Args:
        email (str): Garmin Connect email address
        password (str): Garmin Connect password
    
    Returns:
        garminconnect.Garmin: Authenticated Garmin Connect client instance
        
    Raises:
        garminconnect.GarminConnectAuthenticationError: If authentication fails
        Exception: For any other connection errors
    """
    print(f"Attempting to authenticate with Garmin Connect...")
    print(f"Email: {email}")
    
    try:
        # Initialize Garmin Connect client with credentials
        garmin_client = garminconnect.Garmin(email, password)
        
        # Attempt to authenticate
        print("Calling garmin_client.login()...")
        garmin_client.login()
        print(f"Successfully logged in as: {garmin_client.username}")
        return garmin_client
    
    # Catch specific authentication errors
    except garminconnect.GarminConnectAuthenticationError as auth_error:
        print(f"Garmin authentication failed: {auth_error}")
        print("Possible causes:")
        print("1. Incorrect email or password")
        print("2. Two-factor authentication enabled (not supported by API)")
        print("3. Account locked or requires CAPTCHA verification")
        print("4. Try logging into connect.garmin.com first")
        raise

    # Catch general connection errors
    except Exception as general_error:
        print(f"Unexpected error during login: {general_error}")
        print(f"Error type: {type(general_error).__name__}")
        print("This might be a network issue or Garmin API temporary problem")
        raise


def fetch_running_activities(garmin_client, start_date, end_date):
    """
    Fetch running activities from Garmin Connect for the specified date range.
    
    Args:
        garmin_client (garminconnect.Garmin): Authenticated Garmin Connect client
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    
    Returns:
        list: List of running activity dictionaries from Garmin Connect API
    """
    running_activities = garmin_client.get_activities_by_date(start_date, end_date, "running")
    print(f"Retrieved {len(running_activities)} running activities.")
    return running_activities

def map_splits_to_segments(split_summaries):
    """
    Map split summaries to their corresponding structured segments.
    
    Converts raw splitSummaries data from Garmin Connect into standardized
    segment objects with normalized types and calculated pace metrics.
    
    Args:
        split_summaries (list): List of split dictionaries from Garmin Connect API
                               Each split contains splitType, duration, and averageSpeed
    
    Returns:
        list: List of segment dictionaries with keys:
              - type (str): Normalized segment type (e.g., 'active', 'warmup', 'recovery')
              - duration_sec (int): Segment duration in seconds
              - avg_pace_sec_per_mi (float): Average pace in seconds per mile
              
    Note:
        - Strips prefixes like 'INTERVAL_' and 'RWD_' from splitType
        - Converts 'walk' to 'recovery' for consistency
        - Handles zero speed by returning 0 pace
    """
    segments = []

    for split in split_summaries:
        # Normalize the segment type by converting to lowercase and stripping prefixes
        segment_type = split['splitType']\
            .lower()\
            .replace('interval_', '')\
            .replace('rwd_', '')\
            .replace('walk', 'recovery')

        # Extract duration in seconds
        duration_sec = split.get('duration', 0)

        # Convert average speed to pace (seconds per mile)
        avg_speed = split.get('averageSpeed', 0)
        avg_pace_sec_per_mi = round(1609.344 / avg_speed, 2) if avg_speed > 0 else 0

        # Build segment dictionary
        segment = {
            "type": segment_type,
            "duration_sec": duration_sec,
            "avg_pace_sec_per_mi": avg_pace_sec_per_mi
        }

        segments.append(segment)

    return segments

def transform_activities(activities):
    """
    Transform raw Garmin Connect activity data into standardized format.
    
    Processes each activity to extract key metrics and convert units to a consistent
    format. Includes workout segments if available from splitSummaries data.
    
    Args:
        activities (list): List of raw activity dictionaries from Garmin Connect API
    
    Returns:
        list: List of transformed activity dictionaries with calculated metrics:
              - date: Activity date in YYYY-MM-DD format
              - workout_name: Activity name from Garmin Connect
              - total_time_sec: Duration in seconds
              - total_distance_mi: Distance converted to miles (rounded to 2 decimals)
              - average_pace_sec_per_mile: Calculated pace (rounded to 2 decimals)
              - avg_hr_bpm: Average heart rate if available
              - avg_cadence_spm: Average cadence if available
              - segments: List of workout segments from splits data
    """
    activities_data = []
    
    for activity in activities:
        # Calculate distance in miles with safe division
        distance_miles = activity.get('distance', 0) / METERS_TO_MILES
        duration_seconds = activity.get('duration', 0)
        
        # Calculate average pace (seconds per mile) with safe division
        avg_pace = (duration_seconds / distance_miles) if distance_miles > 0 else 0

        # Build base activity entry
        activity_entry = {
            "date": activity['startTimeLocal'].split(' ')[0],
            "workout_name": activity.get('activityName', 'Unknown'),
            "total_time_sec": duration_seconds,
            "total_distance_mi": round(distance_miles, 2),
            "average_pace_sec_per_mile": round(avg_pace, 2),
            "avg_hr_bpm": activity.get('averageHR'),
            "avg_cadence_spm": activity.get('averageRunningCadenceInStepsPerMinute')
        }
        
        # Extract and process segments from splits data if available
        splits_data = activity.get('splitSummaries', [])
        if splits_data:
            segments = map_splits_to_segments(splits_data)
            activity_entry['segments'] = segments
        else:
            activity_entry['segments'] = []

        activities_data.append(activity_entry)
    
    print(f"Running activities found on dates: {[activity['date'] for activity in activities_data]}")
    return activities_data


def export_to_json(activities_data, output_file):
    """
    Export transformed activities data to JSON file.
    
    Args:
        activities_data (list): List of transformed activity dictionaries
        output_file (str): Path to output JSON file
    """
    output_data = {"running_activities": activities_data}
    with open(output_file, "w") as json_file:
        json.dump(output_data, json_file, indent=2)
    print(f"Running activities data exported to {output_file}")


def run_extraction(config=None):
    """
    Run the complete data extraction workflow.
    
    Args:
        config (Config, optional): Configuration object. If None, creates default config.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    if config is None:
        config = Config()
    
    try:
        # Authenticate with Garmin Connect
        garmin_client = authenticate_garmin(config.garmin_email, config.garmin_password)
        print("Garmin Connect authentication completed successfully.")
        
        # Fetch running activities
        running_activities = fetch_running_activities(garmin_client, config.start_date, config.end_date)
        
        # Transform the data
        activities_data = transform_activities(running_activities)
        
        # Export to JSON
        export_to_json(activities_data, config.output_file)
        
        return 0
    
    except Exception as error:
        print(f"Application failed: {error}")
        return 1
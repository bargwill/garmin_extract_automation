#!/usr/bin/env python3
"""
Garmin Connect Data Extraction Tool

A script to authenticate with Garmin Connect and extract running activity data.
Exports comprehensive running metrics to JSON for analysis.

Author: Your Name
Date: July 31, 2025
Version: 1.0.0
"""

import sys
import json
import os
import garminconnect
from datetime import datetime

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass

# Configuration constants - use environment variables
GARMIN_EMAIL = os.getenv('GARMIN_EMAIL', None)
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD', None)

# Validate that required credentials are provided
if not GARMIN_EMAIL or not GARMIN_PASSWORD:
    raise ValueError("GARMIN_EMAIL and GARMIN_PASSWORD must be set as environment variables.")
# Date range for data extraction
START_DATE = os.getenv('START_DATE', "2025-07-25")
END_DATE = os.getenv('END_DATE', "2025-07-31")

# Output configuration
OUTPUT_FILE = os.getenv('OUTPUT_FILE', "running_activities.json")

# Conversion constants
METERS_TO_MILES = 1609.34


def authenticate_garmin():
    """
    Authenticate with Garmin Connect.
    
    Returns:
        garminconnect.Garmin: Authenticated Garmin Connect client instance
        
    Raises:
        garminconnect.GarminConnectAuthenticationError: If authentication fails
        Exception: For any other connection errors
    """
    try:
        # Initialize Garmin Connect client with credentials
        garmin_client = garminconnect.Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
        
        # Attempt to authenticate
        garmin_client.login()
        print(f"Successfully logged in as: {garmin_client.username}")
        return garmin_client
    
    # Catch specific authentication errors
    except garminconnect.GarminConnectAuthenticationError as auth_error:
        print(f"Authentication failed: {auth_error}")
        raise

    # Catch general connection errors
    except Exception as general_error:
        print(f"Unexpected error during login: {general_error}")
        raise


def main():
    """
    Main entry point for the application.
    
    Authenticates with Garmin Connect, retrieves running activities within the 
    specified date range, and exports comprehensive activity data to JSON.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        # Authenticate with Garmin Connect
        garmin_client = authenticate_garmin()
        
        # If we reach here, authentication was successful
        print("Garmin Connect authentication completed successfully.")
    
    # Handle any exceptions that occur during the authentication process
    except Exception as error:
        print(f"Application failed: {error}")
        return 1

    # Retrieve running activities if authentication was successful
    try:
        running_activities = garmin_client.get_activities_by_date(START_DATE, END_DATE, "running")
        print(f"Retrieved {len(running_activities)} running activities.")

        # Extract relevant fields from each running activity
        activities_data = []
        for activity in running_activities:
            # Calculate distance in miles with safe division
            distance_miles = activity.get('distance', 0) / METERS_TO_MILES
            duration_seconds = activity.get('duration', 0)
            
            # Calculate average pace (seconds per mile) with safe division
            avg_pace = (duration_seconds / distance_miles) if distance_miles > 0 else 0
            
            activity_entry = {
                "date": activity['startTimeLocal'].split(' ')[0],
                "workout_name": activity.get('activityName', 'Unknown'),
                "total_time_sec": duration_seconds,
                "total_distance_mi": round(distance_miles, 2),
                "average_pace_sec_per_mile": round(avg_pace, 2),
                "avg_hr_bpm": activity.get('averageHR'),
                "avg_cadence_spm": activity.get('averageRunningCadenceInStepsPerMinute')
            }
            activities_data.append(activity_entry)
        
        print(f"Running activities found on dates: {[activity['date'] for activity in activities_data]}")

        # Save running activities data to JSON file
        output_data = {"running_activities": activities_data}
        with open(OUTPUT_FILE, "w") as json_file:
            json.dump(output_data, json_file, indent=2)
        print(f"Running activities data exported to {OUTPUT_FILE}")

        return 0
    
    # Handle any exceptions that occur during the retrieval of activities
    except Exception as error:
        print(f"Failed to retrieve running activities: {error}")
        return 1

# Entry point for the script
if __name__ == "__main__":
    sys.exit(main())
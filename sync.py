#!/usr/bin/env python3

import argparse
import os
import pandas as pd
from dotenv import load_dotenv
from garminconnect import GarminConnect


def fetch_workouts():
    """Stub for Garmin API logic"""
    pass


def write_csv(data, path):
    """Stub using DataFrame.to_csv"""
    if data is not None:
        df = pd.DataFrame(data)
        df.to_csv(path, index=False)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Sync Garmin workout data")
    parser.add_argument("--output", default="Training-Log.csv", 
                       help="Output CSV file path (default: Training-Log.csv)")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    garmin_user = os.getenv("GARMIN_USER")
    garmin_pass = os.getenv("GARMIN_PASS")
    slack_webhook = os.getenv("SLACK_WEBHOOK")
    
    # Fetch workouts and write to CSV
    data = fetch_workouts()
    write_csv(data, args.output)


if __name__ == "__main__":
    main()
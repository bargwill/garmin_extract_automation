# Usage Examples

## Basic Usage

### Standard Extraction
Extract running data for the default date range:

```bash
# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run extraction (new modular approach)
python main.py

# Or use original script (compatibility)
python sync.py
```

**Expected Output**:
```
Successfully logged in as: your-username
Garmin Connect authentication completed successfully.
Retrieved 5 running activities.
Running activities found on dates: ['2025-07-25', '2025-07-27', '2025-07-29', '2025-07-30', '2025-07-31']
Running activities data exported to running_activities.json
```

## Configuration Examples

### Custom Date Range
Extract data for a specific month:

**.env**:
```bash
GARMIN_EMAIL=your-email@example.com
GARMIN_PASSWORD=your-password
START_DATE=2025-06-01
END_DATE=2025-06-30
OUTPUT_FILE=june_running_data.json
```

### Single Day Extraction
Extract data for just one day:

**.env**:
```bash
GARMIN_EMAIL=your-email@example.com
GARMIN_PASSWORD=your-password
START_DATE=2025-07-31
END_DATE=2025-07-31
OUTPUT_FILE=single_day_activities.json
```

### Long-term Analysis
Extract an entire year of data:

**.env**:
```bash
GARMIN_EMAIL=your-email@example.com
GARMIN_PASSWORD=your-password
START_DATE=2024-01-01
END_DATE=2024-12-31
OUTPUT_FILE=2024_annual_running_data.json
```

## Sample Output Data

### Typical JSON Structure
```json
{
  "running_activities": [
    {
      "date": "2025-07-25",
      "workout_name": "Morning Easy Run",
      "total_time_sec": 2100.0,
      "total_distance_mi": 4.2,
      "average_pace_sec_per_mile": 500.0,
      "avg_hr_bpm": 142.0,
      "avg_cadence_spm": 178.0
    },
    {
      "date": "2025-07-27",
      "workout_name": "Weekend Long Run",
      "total_time_sec": 3600.0,
      "total_distance_mi": 7.5,
      "average_pace_sec_per_mile": 480.0,
      "avg_hr_bpm": 155.0,
      "avg_cadence_spm": 182.0
    },
    {
      "date": "2025-07-29",
      "workout_name": "Tempo Run",
      "total_time_sec": 1800.0,
      "total_distance_mi": 3.8,
      "average_pace_sec_per_mile": 473.68,
      "avg_hr_bpm": 165.0,
      "avg_cadence_spm": 185.0
    }
  ]
}
```

### Pace Conversion Reference
The tool converts pace to seconds per mile. Here are common pace conversions:

| Minutes:Seconds per Mile | Seconds per Mile |
|-------------------------|------------------|
| 6:00 | 360 |
| 7:00 | 420 |
| 8:00 | 480 |
| 9:00 | 540 |
| 10:00 | 600 |

## Python Module Usage

### Programmatic Access
You can now import and use the functionality programmatically:

```python
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_sync import Config, run_extraction

# Create custom configuration
config = Config()
config.start_date = "2025-07-01"
config.end_date = "2025-07-31"
config.output_file = "july_activities.json"

# Run extraction
exit_code = run_extraction(config)
if exit_code == 0:
    print("Extraction completed successfully")
else:
    print("Extraction failed")
```

### Using Individual Functions
Access specific functionality from the core module:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_sync.core import (
    Config, 
    authenticate_garmin, 
    fetch_running_activities,
    transform_activities,
    export_to_json
)

# Step-by-step extraction
config = Config()

# Authenticate
client = authenticate_garmin(config.garmin_email, config.garmin_password)

# Fetch activities
raw_activities = fetch_running_activities(client, config.start_date, config.end_date)

# Transform data
processed_activities = transform_activities(raw_activities)

# Export
export_to_json(processed_activities, config.output_file)
```

### Python Module Usage
You can now import and use the functionality programmatically:

```python
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_sync import Config, run_extraction

# Create custom configuration
config = Config()
config.start_date = "2025-07-01"
config.end_date = "2025-07-31"
config.output_file = "july_activities.json"

# Run extraction
exit_code = run_extraction(config)
if exit_code == 0:
    print("Extraction completed successfully")
else:
    print("Extraction failed")
```

### Using Individual Functions
Access specific functionality from the core module:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_sync.core import (
    Config, 
    authenticate_garmin, 
    fetch_running_activities,
    transform_activities,
    export_to_json
)

# Step-by-step extraction
config = Config()

# Authenticate
client = authenticate_garmin(config.garmin_email, config.garmin_password)

# Fetch activities
raw_activities = fetch_running_activities(client, config.start_date, config.end_date)

# Transform data
processed_activities = transform_activities(raw_activities)

# Export
export_to_json(processed_activities, config.output_file)
```
Load and analyze the exported data:

```python
import json
import pandas as pd
from datetime import datetime

# Load exported data
with open('running_activities.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame for analysis
df = pd.DataFrame(data['running_activities'])

# Convert pace back to minutes:seconds format
df['pace_min_sec'] = (df['average_pace_sec_per_mile'] / 60).round(2)

# Calculate total weekly mileage
df['date'] = pd.to_datetime(df['date'])
weekly_mileage = df.groupby(df['date'].dt.week)['total_distance_mi'].sum()

print("Weekly Mileage Summary:")
print(weekly_mileage)
```

### Excel/Spreadsheet Import
The JSON format can be easily imported into Excel:

1. Open Excel
2. Data → Get Data → From File → From JSON
3. Select your `running_activities.json` file
4. Excel will automatically parse the structure
5. Load into worksheet for analysis

### Database Integration
Import into SQLite for querying:

```python
import json
import sqlite3
import pandas as pd

# Load JSON data
with open('running_activities.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data['running_activities'])

# Create SQLite database
conn = sqlite3.connect('running_data.db')
df.to_sql('activities', conn, if_exists='replace', index=False)

# Example queries
cursor = conn.cursor()

# Average pace by month
cursor.execute("""
    SELECT strftime('%Y-%m', date) as month, 
           AVG(average_pace_sec_per_mile) as avg_pace
    FROM activities 
    GROUP BY month
    ORDER BY month
""")

results = cursor.fetchall()
for month, avg_pace in results:
    minutes = int(avg_pace // 60)
    seconds = int(avg_pace % 60)
    print(f"{month}: {minutes}:{seconds:02d} per mile")
```

## Automation Examples

### Scheduled Extraction (Windows)
Create a batch file for automated runs:

**extract_weekly.bat**:
```batch
@echo off
cd /d "C:\Users\bargw\Documents\GitHub Repos\garmin_extract_automation"

# Set current week dates
for /f "tokens=1-3 delims=/" %%a in ('date /t') do (
    set START_DATE=2025-07-28
    set END_DATE=2025-08-03
)

python main.py
if %errorlevel% equ 0 (
    echo Weekly extraction completed successfully
) else (
    echo Extraction failed with error %errorlevel%
)
pause
```

### Cron Job (Linux/Mac)
Add to crontab for weekly automation:

```bash
# Extract weekly running data every Sunday at 8 AM
0 8 * * 0 cd /path/to/garmin_extract_automation && python main.py
```

## Troubleshooting Examples

### Debug Mode
Add debug information to understand what's happening:

```python
# Add after successful authentication in main()
print(f"Searching for activities from {START_DATE} to {END_DATE}")
print(f"Username: {garmin_client.username}")

# Add before data processing
print(f"Raw activity count: {len(running_activities)}")
for i, activity in enumerate(running_activities[:3]):  # Show first 3
    print(f"Activity {i+1} keys: {list(activity.keys())}")
```

### Handle Missing Data
Modify the script to handle activities with missing metrics:

```python
# Enhanced data extraction with validation
activity_entry = {
    "date": activity['startTimeLocal'].split(' ')[0],
    "workout_name": activity.get('activityName', 'Unnamed Activity'),
    "total_time_sec": activity.get('duration', 0),
    "total_distance_mi": round(distance_miles, 2) if distance_miles > 0 else None,
    "average_pace_sec_per_mile": round(avg_pace, 2) if avg_pace > 0 else None,
    "avg_hr_bpm": activity.get('averageHR') if activity.get('averageHR', 0) > 0 else None,
    "avg_cadence_spm": activity.get('averageRunningCadenceInStepsPerMinute')
}
```

### Multiple Activity Types
Extract all cardio activities instead of just running:

```python
# In main(), replace the running-specific call:
all_activities = garmin_client.get_activities_by_date(START_DATE, END_DATE)

# Filter for cardio activities
cardio_types = ['running', 'cycling', 'walking']
filtered_activities = [
    activity for activity in all_activities 
    if activity.get('activityType', '').lower() in cardio_types
]
```

## Performance Tips

### Large Date Ranges
For extracting large amounts of data:

1. **Chunk the requests**: Break large date ranges into smaller chunks
2. **Add delays**: Prevent rate limiting with small delays between requests
3. **Cache results**: Store intermediate results to avoid re-processing

### Memory Optimization
For very large datasets:

```python
# Process activities one at a time instead of loading all into memory
def process_activities_streaming(garmin_client, start_date, end_date):
    activities_data = []
    
    # Process in monthly chunks
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    
    while current_date <= end_date_obj:
        month_end = current_date.replace(day=28) + timedelta(days=4)
        month_end = month_end - timedelta(days=month_end.day)
        
        chunk_activities = garmin_client.get_activities_by_date(
            current_date.strftime("%Y-%m-%d"),
            min(month_end, end_date_obj).strftime("%Y-%m-%d"),
            "running"
        )
        
        # Process chunk and append to results
        for activity in chunk_activities:
            # ... processing logic ...
            activities_data.append(activity_entry)
        
        current_date = month_end + timedelta(days=1)
    
    return activities_data
```

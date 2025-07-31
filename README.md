# Garmin Connect Data Extraction Tool

A Python script that authenticates with Garmin Connect and extracts comprehensive running activity data. Exports detailed metrics to JSON format for analysis and visualization.

## Features

- **Secure Authentication**: Uses environment variables for credentials
- **Comprehensive Data**: Extracts key running metrics including pace, distance, heart rate, and cadence
- **Flexible Date Ranges**: Configurable start and end dates for data extraction
- **JSON Export**: Clean, structured output format for easy analysis
- **Error Handling**: Robust error handling for network and authentication issues

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

Copy the example environment file and add your Garmin Connect credentials:

```bash
copy .env.example .env
```

Edit `.env` and add your credentials:
```
GARMIN_EMAIL=your-email@gmail.com
GARMIN_PASSWORD=your-password
START_DATE=2025-07-25
END_DATE=2025-07-31
```

### 3. Run the Tool

```bash
python sync.py
```

## Output

The script generates a `running_activities.json` file with the following structure:

```json
{
  "running_activities": [
    {
      "date": "2025-07-29",
      "workout_name": "Morning Run",
      "total_time_sec": 1800.0,
      "total_distance_mi": 3.5,
      "average_pace_sec_per_mile": 514.29,
      "avg_hr_bpm": 145.0,
      "avg_cadence_spm": 180.0
    }
  ]
}
```

## Data Fields

| Field | Description | Unit |
|-------|-------------|------|
| `date` | Activity date | YYYY-MM-DD |
| `workout_name` | Activity name from Garmin | String |
| `total_time_sec` | Total workout duration | Seconds |
| `total_distance_mi` | Total distance covered | Miles |
| `average_pace_sec_per_mile` | Average pace | Seconds per mile |
| `avg_hr_bpm` | Average heart rate | Beats per minute |
| `avg_cadence_spm` | Average running cadence | Steps per minute |

## Security

- **Environment Variables**: Credentials are stored in `.env` file (not tracked in git)
- **Fallback Support**: Works with or without python-dotenv package
- **No Hardcoded Secrets**: All sensitive data configurable via environment

## Requirements

- Python 3.7+
- Valid Garmin Connect account
- Internet connection for API access

## Troubleshooting

### Authentication Issues
- Verify your Garmin Connect credentials are correct
- Check if your account has two-factor authentication enabled
- Ensure you can log in to Garmin Connect via web browser

### No Activities Found
- Verify the date range includes days with running activities
- Check that activities are synced to Garmin Connect
- Ensure activities are marked as "Running" type

## Version

**v1.0.0** - Initial release with core functionality

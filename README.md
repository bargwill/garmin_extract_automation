# Garmin Connect Data Extraction Tool

A modular Python tool that authenticates with Garmin Connect and extracts comprehensive running activity data. Exports detailed metrics including workout segments to JSON format for analysis and visualization.

## Features

- **Modular Architecture**: Clean separation of concerns with core business logic and CLI interface
- **Comprehensive Data**: Extracts key running metrics including pace, distance, heart rate, cadence, and workout segments
- **Workout Segments**: Detailed segment analysis from split summaries (warmup, active, recovery, cooldown)
- **Secure Authentication**: Uses environment variables for credentials
- **Flexible Date Ranges**: Configurable start and end dates for data extraction
- **JSON Export**: Clean, structured output format for easy analysis
- **Error Handling**: Robust error handling for network and authentication issues
- **Programmatic Access**: Can be imported and used as a Python package

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

**New modular approach (recommended):**
```bash
python main.py
```

**Original script (maintained for compatibility):**
```bash
python sync.py
```

## Architecture

The tool follows a modular architecture:

```
src/garmin_sync/
├── core.py     # Business logic and data operations
├── cli.py      # Command-line interface
└── __init__.py # Package exports

main.py         # Primary entry point
sync.py         # Original script (compatibility)
```

### Programmatic Usage

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_sync import Config, run_extraction

# Custom configuration
config = Config()
config.start_date = "2025-07-01"
config.end_date = "2025-07-31"
config.output_file = "custom_output.json"

# Run extraction
exit_code = run_extraction(config)
```

## Output

The script generates a `running_activities.json` file with the following structure:

```json
{
  "running_activities": [
    {
      "date": "2025-07-31",
      "workout_name": "Morning Run",
      "total_time_sec": 1800.0,
      "total_distance_mi": 3.5,
      "average_pace_sec_per_mile": 514.29,
      "avg_hr_bpm": 145.0,
      "avg_cadence_spm": 180.0,
      "segments": [
        {
          "type": "warmup",
          "duration_sec": 600,
          "avg_pace_sec_per_mi": 665.29
        },
        {
          "type": "active", 
          "duration_sec": 300,
          "avg_pace_sec_per_mi": 402.34
        },
        {
          "type": "recovery",
          "duration_sec": 120,
          "avg_pace_sec_per_mi": 804.90
        },
        {
          "type": "cooldown",
          "duration_sec": 300,
          "avg_pace_sec_per_mi": 536.45
        }
      ]
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
| `segments` | Array of workout segments | Object array |

### Segment Data

Each segment in the `segments` array contains:

| Field | Description | Unit |
|-------|-------------|------|
| `type` | Segment type (warmup, active, recovery, cooldown, run) | String |
| `duration_sec` | Segment duration | Seconds |  
| `avg_pace_sec_per_mi` | Average pace for segment | Seconds per mile |

## Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[Project Overview](docs/project-overview.md)**: High-level project summary and structure
- **[Technical Specifications](docs/technical-specifications.md)**: Detailed API docs and architecture
- **[Usage Examples](docs/usage-examples.md)**: Code samples, integrations, and troubleshooting

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

**v1.0.0** - Current release with modular architecture and segments support

### Changelog
- ✅ Modular architecture with clear separation of concerns  
- ✅ Comprehensive workout segments extraction from splits data
- ✅ Enhanced documentation and code organization
- ✅ Programmatic access via package imports
- ✅ Backward compatibility with original sync.py script
- ✅ Comprehensive test suite for segments functionality

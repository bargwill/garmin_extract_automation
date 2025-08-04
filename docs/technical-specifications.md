# Technical Specifications

## Architecture Overview

The Garmin Extract Automation tool now follows a modular architecture with clear separation of concerns:

### Module Structure

```
src/garmin_sync/
├── core.py     # Business logic and data operations
├── cli.py      # Command-line interface and orchestration  
└── __init__.py # Package exports and initialization

main.py         # Entry point script
sync.py         # Original monolithic script (compatibility)
```

## Core Functions

### `core.py` - Business Logic Module

#### `Config` class
**Purpose**: Manages configuration and environment variable loading

**Attributes**:
- `garmin_email`, `garmin_password`: Authentication credentials
- `start_date`, `end_date`: Data extraction date range
- `output_file`: JSON export file path

**Validation**: Raises `ValueError` if required credentials are missing

#### `authenticate_garmin(email, password)`
**Purpose**: Establishes connection to Garmin Connect API

**Parameters**:
- `email` (str): Garmin Connect email address
- `password` (str): Garmin Connect password

**Process**:
1. Creates `garminconnect.Garmin` client instance
2. Performs login using provided credentials
3. Returns authenticated client or raises exceptions

**Error Handling**:
- `GarminConnectAuthenticationError`: Invalid credentials
- `Exception`: Network or other connection issues

**Returns**: `garminconnect.Garmin` instance

#### `fetch_running_activities(garmin_client, start_date, end_date)`
**Purpose**: Retrieves running activities from Garmin Connect

**Parameters**:
- `garmin_client`: Authenticated Garmin Connect client
- `start_date`, `end_date`: Date range in YYYY-MM-DD format

**Returns**: List of raw activity dictionaries

#### `transform_activities(activities)`
**Purpose**: Converts raw Garmin data to standardized format

**Parameters**:
- `activities`: List of raw activity dictionaries

**Returns**:         list: List of transformed activity dictionaries with calculated metrics:
              - date: Activity date in YYYY-MM-DD format
              - workout_name: Activity name from Garmin Connect
              - total_time_sec: Duration in seconds
              - total_distance_mi: Distance converted to miles (rounded to 2 decimals)
              - average_pace_sec_per_mile: Calculated pace (rounded to 2 decimals)
              - avg_hr_bpm: Average heart rate if available
              - avg_cadence_spm: Average cadence if available
              - segments: List of workout segments from splits data

#### `map_splits_to_segments(split_summaries)`
**Purpose**: Convert split summaries to structured segment data

**Parameters**:
- `split_summaries`: List of split dictionaries from Garmin Connect API

**Returns**: List of segment dictionaries with normalized types and calculated pace metrics

**Processing**:
- Normalizes segment types by removing prefixes and converting to lowercase
- Converts 'walk' segments to 'recovery' for consistency
- Calculates pace from average speed with safe division

#### `export_to_json(activities_data, output_file)`
**Purpose**: Exports transformed data to JSON file

**Parameters**:
- `activities_data`: List of transformed activities
- `output_file`: Output file path

#### `run_extraction(config=None)`
**Purpose**: Orchestrates the complete extraction workflow

**Parameters**:
- `config`: Configuration object (creates default if None)

**Returns**: Exit code (0=success, 1=failure)

### `cli.py` - Command-Line Interface Module

#### `setup_logging()`
**Purpose**: Configures basic logging for the application

#### `main()`
**Purpose**: Main CLI entry point that orchestrates the workflow

**Process**:
1. Sets up logging
2. Creates configuration
3. Calls `core.run_extraction()`
4. Returns appropriate exit codes

**Returns**: Exit code (0=success, 1=failure)

## Data Transformation Pipeline

### Input Data (Garmin Connect API)
Raw activity objects contain extensive metadata. Key fields accessed:
- `startTimeLocal`: Activity timestamp
- `activityName`: User-defined workout name  
- `distance`: Distance in meters
- `duration`: Duration in seconds
- `averageHR`: Average heart rate
- `averageRunningCadenceInStepsPerMinute`: Cadence

### Processing Logic
```python
# Distance conversion
distance_miles = activity.get('distance', 0) / METERS_TO_MILES

# Pace calculation (with safe division)
avg_pace = (duration_seconds / distance_miles) if distance_miles > 0 else 0

# Date extraction
date = activity['startTimeLocal'].split(' ')[0]  # YYYY-MM-DD format
```

### Output Schema
```json
{
  "running_activities": [
    {
      "date": "string (YYYY-MM-DD)",
      "workout_name": "string",
      "total_time_sec": "number",
      "total_distance_mi": "number (rounded to 2 decimals)",
      "average_pace_sec_per_mile": "number (rounded to 2 decimals)", 
      "avg_hr_bpm": "number|null",
      "avg_cadence_spm": "number|null",
      "segments": [
        {
          "type": "string (warmup|active|recovery|cooldown|run)",
          "duration_sec": "number",
          "avg_pace_sec_per_mi": "number (rounded to 2 decimals)"
        }
      ]
    }
  ]
}
```

## Configuration Management

### Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GARMIN_EMAIL` | Yes | None | Garmin Connect email |
| `GARMIN_PASSWORD` | Yes | None | Garmin Connect password |
| `START_DATE` | No | "2025-07-25" | Data extraction start date |
| `END_DATE` | No | "2025-07-31" | Data extraction end date |
| `OUTPUT_FILE` | No | "running_activities.json" | Output filename |

### Constants
```python
METERS_TO_MILES = 1609.344  # Conversion factor for distance
```

## API Dependencies

### Garmin Connect (garminconnect==0.2.28)
**Purpose**: Unofficial Python library for Garmin Connect API access

**Key Methods Used**:
- `Garmin(email, password)`: Client initialization
- `login()`: Authentication
- `get_activities_by_date(start, end, activity_type)`: Activity retrieval

**Rate Limits**: Inherits Garmin Connect web API limitations

### Python-dotenv (python-dotenv==1.0.0) 
**Purpose**: Environment variable loading from `.env` files

**Implementation**: Graceful fallback if not installed
```python
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Continue without dotenv
```

## Error Handling Strategy

### Authentication Errors
- Specific handling for `GarminConnectAuthenticationError`
- Clear error messages for credential issues
- Application exits with code 1 on auth failure

### Data Processing Errors
- Safe division for pace calculations
- Default values for missing activity fields
- Graceful handling of malformed responses

### File I/O Errors
- JSON export wrapped in try/catch blocks
- Clear error messages for file write issues

## Performance Considerations

### API Efficiency
- Single API call for date range (vs. individual date requests)
- Filters to running activities only
- Minimal data processing overhead

### Memory Usage
- Processes activities in single list (suitable for typical use cases)
- JSON serialization handles large datasets efficiently

### Scalability Limits
- Single-threaded execution
- Memory bound by activity count in date range
- No pagination handling (Garmin API dependent)

## Security Implementation

### Credential Protection
- Environment variables prevent hardcoded secrets
- `.env` file excluded from version control
- No credential logging or console output

### API Security
- Uses official garminconnect library
- Inherits SSL/TLS from underlying HTTP library
- No credential storage or caching

## Extension Points

The current architecture supports extension in several areas:

1. **Additional Activity Types**: Modify activity filter parameter
2. **Enhanced Metrics**: Process additional fields from raw activity data
3. **Multiple Output Formats**: Add CSV, Excel, or database export options
4. **Date Range Logic**: Implement relative date ranges or recurring schedules
5. **Data Validation**: Add schema validation for exported data

# Refactored Architecture Guide

## Overview

The Garmin Extract Automation tool has been refactored into a modular architecture that makes it much easier to extend functionality and add new data fields to the output JSON. This guide explains the new structure and how to work with it.

## New Architecture

### Module Structure

```
src/garmin_sync/
├── __init__.py          # Package exports and initialization
├── cli.py               # Command-line interface (unchanged)
├── core.py              # Main workflow orchestration
├── api_client.py        # Garmin Connect API operations
├── data_processor.py    # Data transformation and export
└── models.py            # Data models and classes
```

### Key Improvements

1. **Separation of Concerns**: Each module has a single responsibility
2. **Type Safety**: Full type annotations and data models
3. **Extensibility**: Easy to add new data fields and processing steps
4. **Testability**: Modular design allows for comprehensive unit testing
5. **Backward Compatibility**: Legacy functions still work with deprecation warnings

## Core Components

### 1. Models (`models.py`)

**Purpose**: Define structured data classes for type safety and consistency.

**Key Classes**:
- `Segment`: Represents workout segments (warmup, active, recovery, etc.)
- `Activity`: Represents complete running activities with all metrics
- `ExtractionResult`: Container for complete extraction with metadata

**Benefits**:
- Type safety prevents runtime errors
- Clear data structure makes extending easy
- Automatic validation and conversion methods

### 2. API Client (`api_client.py`)

**Purpose**: Handle all Garmin Connect API interactions.

**Key Classes**:
- `GarminClient`: Wrapper for Garmin Connect operations
- Factory function `create_authenticated_client()`

**Benefits**:
- Centralized error handling
- Clean interface for API operations
- Easy to mock for testing

### 3. Data Processor (`data_processor.py`)

**Purpose**: Transform raw API data into structured models and handle exports.

**Key Classes**:
- `DataProcessor`: Handles all data transformation operations

**Key Functions**:
- `transform_activities()`: Convert raw data to Activity models
- `create_extraction_result()`: Add metadata to results
- `filter_activities_by_criteria()`: Apply filters to activities
- `export_to_json()`: Export with enhanced metadata
- `export_to_csv()`: Optional CSV export (requires pandas)

### 4. Core Orchestration (`core.py`)

**Purpose**: Coordinate the complete workflow using other modules.

**Key Functions**:
- `run_extraction()`: Main workflow orchestration
- `Config`: Enhanced configuration management

## Enhanced Output Format

The new output includes metadata and additional fields:

```json
{
  "extraction_metadata": {
    "extraction_date": "2025-08-05T14:40:38.261895",
    "date_range": {
      "start_date": "2025-07-31",
      "end_date": "2025-07-31"
    },
    "total_activities": 1
  },
  "running_activities": [
    {
      "date": "2025-07-31",
      "workout_name": "North Providence - Run",
      "total_time_sec": 1488.19,
      "total_distance_mi": 2.29,
      "average_pace_sec_per_mile": 649.93,
      "avg_hr_bpm": 146.0,
      "avg_cadence_spm": 151.078125,
      "segments": [...],
      "activity_id": "19910941482",
      "start_time": "2025-07-31 18:06:08",
      "calories": 350.0,
      "elevation_gain_ft": 72.2,
      "max_hr_bpm": 162.0
    }
  ]
}
```

## How to Add New Data Fields

### Step 1: Update the Activity Model

Edit `src/garmin_sync/models.py` and add new fields to the `Activity` dataclass:

```python
@dataclass
class Activity:
    # ... existing fields ...
    
    # NEW FIELDS - Add here
    avg_power_watts: Optional[int] = None
    normalized_power: Optional[int] = None
    training_effect: Optional[float] = None
    weather_conditions: Optional[str] = None
```

### Step 2: Update the from_garmin_data Method

In the same file, update the `from_garmin_data` class method to extract the new data:

```python
@classmethod
def from_garmin_data(cls, activity_data: Dict[str, Any]) -> 'Activity':
    # ... existing extraction logic ...
    
    return cls(
        # ... existing fields ...
        
        # NEW FIELDS - Extract from API data
        avg_power_watts=activity_data.get('avgPower'),
        normalized_power=activity_data.get('normalizedPower'),
        training_effect=activity_data.get('trainingEffect'),
        weather_conditions=activity_data.get('weatherCondition')
    )
```

### Step 3: Update the to_dict Method

Add the new fields to the dictionary output:

```python
def to_dict(self) -> Dict[str, Any]:
    # ... existing fields ...
    
    # Add new optional fields to the list
    optional_fields = [
        'activity_id', 'start_time', 'calories', 
        'elevation_gain_ft', 'max_hr_bpm', 'training_stress_score',
        # NEW FIELDS
        'avg_power_watts', 'normalized_power', 'training_effect', 'weather_conditions'
    ]
    
    # ... rest of method unchanged ...
```

### Step 4: Update Tests

Add test cases in `tests/test_refactored.py` to verify your new fields work correctly.

## Advanced Extensions

### Adding Data Enrichment

You can enrich activities with additional API calls:

```python
# In data_processor.py
def enrich_with_detailed_data(self, activity: Activity, garmin_client: GarminClient) -> Activity:
    """Fetch additional detailed data for an activity."""
    if activity.activity_id:
        detailed_data = garmin_client.get_activity_details(activity.activity_id)
        if detailed_data:
            # Add more detailed information
            additional_data = {
                'training_stress_score': detailed_data.get('trainingStressScore'),
                'weather_conditions': detailed_data.get('weatherCondition')
            }
            return self.enrich_activity_data(activity, additional_data)
    return activity
```

### Adding Custom Filtering

Create custom filters in `data_processor.py`:

```python
def filter_by_performance_metrics(
    self, 
    activities: List[Activity],
    min_avg_hr: Optional[int] = None,
    max_pace: Optional[float] = None
) -> List[Activity]:
    """Filter activities by performance criteria."""
    filtered = activities.copy()
    
    if min_avg_hr:
        filtered = [a for a in filtered if a.avg_hr_bpm and a.avg_hr_bpm >= min_avg_hr]
    
    if max_pace:
        filtered = [a for a in filtered if a.average_pace_sec_per_mile <= max_pace]
    
    return filtered
```

### Adding New Export Formats

Add new export functions to `data_processor.py`:

```python
def export_to_excel(extraction_result: ExtractionResult, output_file: str) -> None:
    """Export to Excel with multiple sheets."""
    try:
        import pandas as pd
        
        # Create summary sheet
        summary_data = [activity.to_dict() for activity in extraction_result.activities]
        summary_df = pd.DataFrame(summary_data)
        
        # Create segments sheet
        segments_data = []
        for activity in extraction_result.activities:
            for segment in activity.segments or []:
                segments_data.append({
                    'activity_date': activity.date,
                    'activity_name': activity.workout_name,
                    'segment_type': segment.type,
                    'duration_sec': segment.duration_sec,
                    'avg_pace_sec_per_mi': segment.avg_pace_sec_per_mi
                })
        
        segments_df = pd.DataFrame(segments_data)
        
        # Write to Excel with multiple sheets
        with pd.ExcelWriter(output_file) as writer:
            summary_df.to_excel(writer, sheet_name='Activities', index=False)
            segments_df.to_excel(writer, sheet_name='Segments', index=False)
            
        logger.info(f"Exported to Excel: {output_file}")
        
    except ImportError:
        logger.error("pandas and openpyxl required for Excel export")
        raise
```

## Configuration Options

New environment variables you can set:

- `INCLUDE_METADATA`: Set to `false` to use legacy output format
- `OUTPUT_FORMAT`: Future support for different output formats
- `ENABLE_ENRICHMENT`: Enable additional API calls for detailed data

## Migration Guide

### For Existing Scripts

The refactored code maintains backward compatibility. Existing scripts will continue to work but may show deprecation warnings. To update:

**Old way:**
```python
from garmin_sync.core import authenticate_garmin, fetch_running_activities, transform_activities

client = authenticate_garmin(email, password)
activities = fetch_running_activities(client, start_date, end_date)
transformed = transform_activities(activities)
```

**New way:**
```python
from garmin_sync import create_authenticated_client, DataProcessor

client = create_authenticated_client(email, password)
raw_activities = client.get_running_activities(start_date, end_date)
processor = DataProcessor()
activities = processor.transform_activities(raw_activities)
```

### For Testing

The new modular structure makes testing much easier:

```python
from garmin_sync.models import Activity
from garmin_sync.data_processor import DataProcessor

# Easy to create test data
test_activity = Activity(
    date="2025-08-05",
    workout_name="Test Run",
    total_time_sec=1800,
    total_distance_mi=3.0,
    average_pace_sec_per_mile=600.0
)

# Easy to test individual components
processor = DataProcessor()
result = processor.create_extraction_result([test_activity], "2025-08-01", "2025-08-07")
```

## Benefits of the Refactored Architecture

1. **Easy Extension**: Adding new data fields requires changes in only 2-3 places
2. **Type Safety**: Catch errors at development time, not runtime
3. **Better Testing**: Each component can be tested independently
4. **Maintainability**: Clear separation makes code easier to understand and modify
5. **Flexibility**: Support for different output formats and filtering options
6. **Performance**: Only fetch additional data when needed
7. **Documentation**: Clear interfaces make the code self-documenting

## Next Steps

With this refactored architecture, you can now easily:

1. Add any new fields from the Garmin Connect API
2. Implement custom data processing and filtering
3. Add new export formats (CSV, Excel, etc.)
4. Create specialized analysis tools
5. Add caching and performance optimizations
6. Implement data validation and quality checks

The modular design makes all of these extensions straightforward and maintainable.

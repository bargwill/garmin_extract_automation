# Garmin Extract Automation - Project Overview

## Purpose
This repository contains a Python automation tool designed to extract running activity data from Garmin Connect and export it to structured JSON format for analysis. The tool is ideal for runners who want to analyze their training data programmatically or integrate it with other systems.

## Repository Structure

```
garmin_extract_automation/
├── src/                           # Source code directory
│   └── garmin_sync/              # Main package
│       ├── __init__.py           # Package initialization
│       ├── core.py              # Business logic and Garmin Connect operations
│       └── cli.py               # Command-line interface and orchestration
├── docs/                         # Documentation directory
│   ├── project-overview.md       # This file - high-level project summary
│   ├── technical-specifications.md # Technical details and API documentation
│   └── usage-examples.md        # Code examples and common use cases
├── .env.example                 # Template for environment variables
├── .gitignore                   # Git ignore rules
├── main.py                      # Main entry point script
├── pyproject.toml              # Project configuration and dependencies
├── README.md                    # Main project documentation
├── requirements.txt             # Python dependencies (legacy)
└── sync.py                     # Original script (maintained for compatibility)
```

## Key Components

### Core Package (`src/garmin_sync/`)
- **core.py**: Contains all business logic including authentication, data fetching, transformation, and export
- **cli.py**: Provides command-line interface and orchestrates the workflow
- **__init__.py**: Package initialization and exports

### Entry Points
- **main.py**: Primary entry point that imports and runs the CLI
- **sync.py**: Original monolithic script (maintained for compatibility)

### Configuration
- **Environment Variables**: Secure credential management via `.env` file
- **Flexible Parameters**: Configurable date ranges and output settings
- **Fallback Support**: Works with or without optional dependencies

### Dependencies (`requirements.txt`)
- **garminconnect**: Official Garmin Connect API library
- **python-dotenv**: Environment variable management (optional)

## Target Use Cases

1. **Personal Analytics**: Extract your own running data for analysis
2. **Training Analysis**: Build custom dashboards and reports
3. **Data Integration**: Feed running data into other systems or databases
4. **Research Projects**: Collect running metrics for academic or personal research
5. **Backup & Archive**: Create local copies of your Garmin Connect data

## Data Output Format

The tool exports running activities as structured JSON with these key metrics:
- Date and workout name
- Duration and distance (converted to miles)
- Average pace (calculated in seconds per mile)
- Heart rate and cadence averages
- **Workout segments** with detailed breakdown of warmup, active, recovery, and cooldown phases

## New in v1.0.0

- **Modular Architecture**: Separated business logic from CLI interface
- **Segments Support**: Extracts detailed workout segment data from split summaries
- **Enhanced Documentation**: Comprehensive docs in dedicated folder
- **Programmatic Access**: Can be imported and used as Python package
- **Backward Compatibility**: Original sync.py maintained for existing workflows

## Security Features

- Environment variable-based credential storage
- No hardcoded secrets in source code
- Git ignores sensitive configuration files
- Optional dependency handling for security libraries

## Technology Stack

- **Language**: Python 3.7+
- **API**: Garmin Connect unofficial API
- **Data Format**: JSON output
- **Configuration**: Environment variables
- **Dependencies**: Minimal external dependencies

## Development Status

**Current Version**: v1.0.0
- ✅ Core authentication and data extraction
- ✅ JSON export functionality
- ✅ Error handling and validation
- ✅ Documentation and examples

## Quick Start Summary

1. Install Python dependencies: `pip install -r requirements.txt`
2. Configure credentials in `.env` file
3. Run extraction: `python main.py` or `python sync.py` (compatibility)
4. Find results in `running_activities.json`

This tool provides a foundation for automating Garmin Connect data extraction and can be extended for more advanced analytics or integration scenarios.

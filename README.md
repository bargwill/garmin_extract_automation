# Garmin Extract Automation

Automated Garmin Connect data synchronization with training analytics and Slack notifications.

This project extracts activity data from Garmin Connect, calculates training load metrics (ACWR and Monotony), exports structured CSV reports, and sends intelligent alerts via Slack to help monitor training patterns and recovery needs.

## Features

- 🏃 **Automated Garmin Sync**: Fetch workout data from Garmin Connect API
- 📊 **Training Analytics**: Calculate ACWR (Acute:Chronic Workload Ratio) and Monotony indices
- 📈 **CSV Export**: Generate structured Training-Log.csv for further analysis
- 🔔 **Slack Notifications**: Send formatted workout summaries with training insights
- 🛡️ **Robust Error Handling**: Comprehensive logging and graceful failure management
- 🧪 **Full Test Coverage**: Unit and integration tests with pytest

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd garmin_extract_automation
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your Garmin Connect and Slack credentials

# Run sync
python sync.py --output Training-Log.csv
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Garmin Connect account
- (Optional) Slack workspace with incoming webhooks

### Setup Steps

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```bash
   GARMIN_USER=your_email@example.com
   GARMIN_PASS=your_password
   SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

## Usage

### Basic Sync
```bash
# Sync last 30 days (default)
python sync.py

# Custom output file
python sync.py --output weekly-report.csv

# Custom date range
python sync.py --start-date 2024-01-01 --end-date 2024-01-31

# Skip Slack notifications
python sync.py --skip-slack

# Verbose logging
python sync.py --verbose
```

### Command Line Options
```
--output PATH        Output CSV file path (default: Training-Log.csv)
--start-date DATE    Start date in YYYY-MM-DD format
--end-date DATE      End date in YYYY-MM-DD format  
--skip-slack         Skip Slack notifications
--verbose, -v        Enable verbose logging
--help, -h           Show help message
```

### Example Workflow
```bash
# Weekly sync with Slack notifications
python sync.py --start-date 2024-01-15 --end-date 2024-01-21 --output weekly.csv

# Monthly analysis without notifications
python sync.py --start-date 2024-01-01 --end-date 2024-01-31 --skip-slack
```

## Training Metrics

### ACWR (Acute:Chronic Workload Ratio)
- **Formula**: 7-day training load ÷ 28-day average training load
- **Interpretation**:
  - < 0.8: Low training load (consider increasing)
  - 0.8-1.3: Optimal training zone
  - > 1.3: High injury risk (consider recovery)

### Monotony Index
- **Formula**: Weekly mean workload ÷ weekly standard deviation
- **Interpretation**:
  - Lower values: More varied training (better)
  - Higher values: Repetitive training (injury risk)

## Output Format

The generated CSV contains:
- `date`: Activity date
- `distance`: Distance in kilometers
- `duration`: Duration in minutes
- `activity_type`: Type of activity (running, cycling, etc.)
- `calories`: Calories burned
- `avg_speed`: Average speed
- `elevation_gain`: Elevation gain in meters

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_analytics.py -v
```

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .
pylint **/*.py
```

### Project Structure
```
├── sync.py              # Main CLI script
├── garmin_client.py     # Garmin Connect API client
├── analytics.py         # Training metrics calculations
├── slack_notify.py      # Slack notification handler
├── config.py            # Configuration management
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── .github/workflows/   # CI/CD pipeline
```

## Troubleshooting

### Common Issues

**Authentication Failed**
```bash
# Verify credentials in .env file
python -c "from config import get_garmin_credentials; print('Credentials OK')"
```

**No Data Retrieved**
- Check date range (activities must exist in specified period)
- Verify Garmin Connect has activities for the date range
- Try a broader date range: `--start-date 2024-01-01`

**Slack Notifications Not Working**
- Verify webhook URL in `.env`
- Test with `--skip-slack` flag first
- Check Slack webhook configuration

**Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Debugging
```bash
# Enable verbose logging
python sync.py --verbose

# Test individual components
python -c "from garmin_client import fetch_workouts; print('Garmin client OK')"
python -c "from analytics import create_sample_data; print('Analytics OK')"
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Run tests: `pytest`
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [python-garminconnect](https://github.com/cyberjunky/python-garminconnect) - Garmin Connect API wrapper
- [Slack SDK](https://github.com/slackapi/python-slack-sdk) - Slack integration

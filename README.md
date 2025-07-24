# garmin_extract_automation

This project automates the process of syncing Garmin fitness data and generating training analytics. It extracts activity data from Garmin Connect, processes it into a structured Training-Log.csv format, calculates key training metrics like ACWR (Acute:Chronic Workload Ratio) and Monotony indices, and sends automated alerts via Slack to help monitor training load and recovery patterns.

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the sync script to extract Garmin data and generate your training log:

```bash
python sync.py --output Training-Log.csv
```

## Configuration

Configure your Slack webhook URL in a `.env` file in the project root:

```
SLACK_WEBHOOK_URL=your_webhook_url_here
```

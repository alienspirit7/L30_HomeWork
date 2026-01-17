# Email Coordinator

Level 1 domain coordinator for all email-related operations.

## Overview

Coordinates email operations by delegating to Level 2 managers:
- **Email Reader**: Fetches and parses incoming emails from Gmail
- **Draft Manager**: Creates personalized email draft replies

## Installation

```bash
cd orchestrator/email_coordinator
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to configure:
- Child manager paths
- Logging settings

## Usage

### Standalone Execution
```bash
# Health check
python -m email_coordinator --action health

# Read emails
python -m email_coordinator --action read_emails --mode test

# With batch size
python -m email_coordinator --action read_emails --mode batch --batch-size 10
```

### As Library
```python
from email_coordinator.coordinator import EmailCoordinator

coordinator = EmailCoordinator(config_path="config.yaml")

# Read emails
result = coordinator.read_emails(mode="test", batch_size=1)

# Create drafts
result = coordinator.create_drafts(email_records, feedback_records)
```

## Actions

| Action | Description | Output |
|--------|-------------|--------|
| `read_emails` | Fetch and parse emails | file_1_2.xlsx |
| `create_drafts` | Create Gmail drafts | Gmail drafts |
| `full_pipeline` | Both operations | Both outputs |

## Project Structure

```
email_coordinator/
├── coordinator.py       # Main coordinator
├── config.yaml         # Configuration
├── requirements.txt    # Dependencies
├── PRD.md             # Product requirements
├── README.md          # This file
├── email_reader/      # Level 2 - Inbound emails
└── draft_manager/     # Level 2 - Outbound drafts
```

## Testing

```bash
python -m pytest tests/ -v
```

## Logging

Logs: `./logs/email_coordinator.log`

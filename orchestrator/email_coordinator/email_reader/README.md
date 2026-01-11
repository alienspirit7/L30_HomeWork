# Email Reader Manager

**Level 2 - Task Manager**

The Email Reader Manager orchestrates inbound email processing by fetching emails from Gmail and parsing them into structured records for homework submission tracking.

## Overview

**Level:** 2 (Task Manager)
**Parent:** Email Coordinator (`../`)
**Children:**
- Gmail Reader (`./gmail_reader/`) - Fetches raw emails from Gmail API
- Email Parser (`./email_parser/`) - Extracts structured data from emails

This manager coordinates two leaf services to read and process homework submission emails, producing a structured Excel file with validated email records.

## Features

- Orchestrates Gmail email fetching and parsing
- Generates unique email identifiers (SHA-256)
- Extracts GitHub repository URLs from email bodies
- Validates email content against homework submission patterns
- Produces structured Excel output (file_1_2.xlsx)
- Supports multiple processing modes (test, batch, full)
- Comprehensive logging and error handling
- Status tracking (Ready vs Missing fields)

## Architecture

```
Email Reader Manager (Level 2)
├── Gmail Reader (Level 3 - Leaf)
│   └── Fetches emails from Gmail API
└── Email Parser (Level 3 - Leaf)
    └── Parses raw emails into structured records
```

## Installation

### 1. Prerequisites

- Python 3.9+
- Gmail API credentials (OAuth 2.0)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Child Services

Both child services need to be configured:

#### Gmail Reader Setup
```bash
cd gmail_reader
pip install -r requirements.txt
```

Download Gmail API credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project and enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Save as `./gmail_reader/data/credentials/credentials.json`

#### Email Parser Setup
```bash
cd email_parser
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to customize settings:

```yaml
manager:
  name: email_reader
  version: "1.0.0"

children:
  gmail_reader: "./gmail_reader"
  email_parser: "./email_parser"

output:
  file_path: "./data/output/file_1_2.xlsx"

logging:
  level: INFO
  file: "./logs/email_reader.log"
```

## Directory Structure

```
email_reader/
├── gmail_reader/              # Gmail API integration (Level 3)
│   ├── service.py
│   ├── config.yaml
│   ├── requirements.txt
│   ├── data/
│   │   └── credentials/
│   │       ├── credentials.json
│   │       └── token.json
│   └── README.md
├── email_parser/              # Email parsing logic (Level 3)
│   ├── src/
│   │   └── email_parser.py
│   ├── config.yaml
│   ├── requirements.txt
│   └── README.md
├── data/
│   └── output/
│       └── file_1_2.xlsx      # Generated output
├── logs/
│   └── email_reader.log       # Manager logs
├── config.yaml                # Manager configuration
├── requirements.txt           # Manager dependencies
├── PRD.md                     # Product Requirements
└── README.md                  # This file
```

## Usage

### As a Standalone Module

```bash
cd orchestrator/email_coordinator/email_reader
python -m manager --mode test
```

### From Parent Service

```python
from email_reader import EmailReaderManager

# Initialize manager
manager = EmailReaderManager(config_path="config.yaml")

# Process emails
input_data = {
    "mode": "batch",
    "batch_size": 50
}

result = manager.process(input_data)

# Access results
print(f"Processed: {result['processed_count']}")
print(f"Ready: {result['ready_count']}")
print(f"Failed: {result['failed_count']}")
print(f"Output: {result['output_file']}")
```

## Input Specification

**From Parent (Email Coordinator):**

```python
{
    "mode": str,          # "test" | "batch" | "full"
    "batch_size": int     # Number of emails to fetch
}
```

## Output Specification

**To Parent (Email Coordinator):**

```python
{
    "emails": List[EmailRecord],
    "output_file": str,         # Path to file_1_2.xlsx
    "processed_count": int,
    "ready_count": int,         # Emails with status="Ready"
    "failed_count": int         # Emails with missing fields
}
```

**Excel Output (file_1_2.xlsx):**

| Column | Type | Description |
|--------|------|-------------|
| email_id | str | SHA-256 hash identifier |
| message_id | str | Gmail message ID (for reply threading) |
| email_datetime | str | Timestamp of email |
| email_subject | str | Email subject line |
| repo_url | str | GitHub repository URL |
| status | str | "Ready" or "Missing: [fields]" |
| hashed_email_address | str | SHA-256 of sender |
| sender_email | str | Original sender email |
| thread_id | str | Gmail thread ID |

## Processing Workflow

1. **Fetch Emails**: Call `gmail_reader.execute()` with search query and max results
2. **Parse Each Email**: For each raw email, call `email_parser.execute()`
3. **Collect Records**: Aggregate all parsed EmailRecord objects
4. **Write Output**: Save records to `file_1_2.xlsx`
5. **Return Summary**: Provide processing statistics to parent

## Processing Modes

### Test Mode
```bash
python -m manager --mode test
```
Fetches and processes 5 emails for testing.

### Batch Mode
```bash
python -m manager --mode batch --batch-size 50
```
Processes specified number of emails.

### Full Mode
```bash
python -m manager --mode full
```
Processes all unread homework submission emails.

## Email Search Pattern

Default Gmail search query:
```
subject:(self check of homework) is:unread
```

Matches:
- "Self Check of Homework 5"
- "SELF CHECK OF HOMEWORK 42"
- "self check of homework 123"

## Data Validation

### Ready Status
Email marked as "Ready" when:
- GitHub repository URL found
- Sender email present
- Valid homework subject pattern

### Missing Status
Email marked as "Missing: [fields]" when:
- No GitHub URL found in body
- Invalid subject pattern
- Missing required fields

Example: `"Missing: repo_url"`

## Testing

Run all tests:
```bash
python -m pytest tests/ -v
```

Test child services:
```bash
cd gmail_reader && python -m pytest tests/ -v
cd email_parser && python -m pytest tests/ -v
```

## Logging

Logs are written to:
- **File:** `./logs/email_reader.log`
- **Level:** INFO (configurable)
- **Format:** `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

Child services maintain their own logs:
- `./gmail_reader/logs/gmail_reader.log`
- `./email_parser/logs/email_parser.log`

## Error Handling

The manager handles:
- Gmail API failures (delegated to gmail_reader)
- Email parsing errors (delegated to email_parser)
- File I/O errors (Excel writing)
- Missing child service configurations
- Invalid input parameters

All errors are logged with details. Processing continues for remaining emails even if individual emails fail.

## Dependencies

### Direct Dependencies
- `openpyxl>=3.1.0` - Excel file generation

### Child Service Dependencies
- Gmail Reader: Google API client libraries
- Email Parser: PyYAML, pytest

### Shared Utilities (if applicable)
- `shared.models.email_data`
- `shared.utils.file_utils`
- `shared.interfaces.coordinator_interface`

## Child Services

### Gmail Reader
**Path:** `./gmail_reader/`
**Purpose:** Fetches raw emails from Gmail API matching homework submission patterns.
**Documentation:** [gmail_reader/README.md](./gmail_reader/README.md)

Key features:
- OAuth2 authentication
- Gmail query search
- Email metadata extraction
- Automatic token refresh

### Email Parser
**Path:** `./email_parser/`
**Purpose:** Extracts structured data from raw email content.
**Documentation:** [email_parser/README.md](./email_parser/README.md)

Key features:
- Email ID generation (SHA-256)
- GitHub URL extraction
- Subject pattern validation
- Field validation

## Standalone Operation

To use email_reader as a completely standalone module:

1. **Install all dependencies:**
   ```bash
   pip install -r requirements.txt
   cd gmail_reader && pip install -r requirements.txt
   cd ../email_parser && pip install -r requirements.txt
   ```

2. **Configure Gmail credentials:**
   ```bash
   # Place credentials.json in gmail_reader/data/credentials/
   ```

3. **Run the manager:**
   ```bash
   python -m manager --mode test
   ```

4. **Check output:**
   ```bash
   ls -la data/output/file_1_2.xlsx
   ```

## Troubleshooting

### Gmail Authentication Issues
**Problem:** Cannot authenticate with Gmail
- Navigate to `gmail_reader/`
- Delete `data/credentials/token.json`
- Re-run to re-authenticate
- See [gmail_reader/README.md](./gmail_reader/README.md) for details

### Missing Output File
**Problem:** file_1_2.xlsx not generated
- Check logs in `./logs/email_reader.log`
- Verify `data/output/` directory exists
- Ensure openpyxl is installed

### Parsing Failures
**Problem:** All emails marked as "Missing: repo_url"
- Verify email body contains GitHub URLs
- Check pattern configuration in `email_parser/config.yaml`
- Test parser independently (see email_parser/README.md)

### Import Errors
**Problem:** Cannot import child services
- Verify child service directories exist
- Check `__init__.py` files are present
- Ensure PYTHONPATH includes email_reader directory

## Version

Current version: **1.0.0**

## Parent Service

This manager is designed to be called by the **Email Coordinator** service located at `../`.

## Related Documentation

- [PRD.md](./PRD.md) - Product Requirements Document
- [gmail_reader/README.md](./gmail_reader/README.md) - Gmail Reader documentation
- [gmail_reader/PRD.md](./gmail_reader/PRD.md) - Gmail Reader requirements
- [email_parser/README.md](./email_parser/README.md) - Email Parser documentation
- [email_parser/PRD.md](./email_parser/PRD.md) - Email Parser requirements

## License

Part of the L30 Homework Orchestrator System.

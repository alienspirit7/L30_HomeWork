# Email Parser Service

**Level 3 - Leaf Service**

Extracts structured data from raw email content. Parses subject, body, GitHub URLs, and validates required fields.

## Overview

The Email Parser Service is a leaf service (no external API dependencies) that processes raw email data into structured format with validation. It generates unique identifiers, extracts GitHub repository URLs, and validates email content against expected patterns.

## Features

- **Email ID Generation**: SHA-256 hash based on sender, subject, and datetime
- **GitHub URL Extraction**: Supports multiple GitHub URL formats
- **Subject Validation**: Pattern matching for homework submission emails
- **Field Validation**: Checks for required fields and reports missing data
- **Comprehensive Logging**: Detailed logging to file and console

## Directory Structure

```
email_parser/
├── src/
│   ├── __init__.py
│   └── email_parser.py      # Core parser implementation
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   └── test_email_parser.py # Test suite (28 tests)
├── logs/
│   └── email_parser.log     # Auto-generated log file
├── venv/                    # Virtual environment
├── __main__.py              # Standalone execution entry point
├── config.yaml              # Service configuration
├── requirements.txt         # Python dependencies
├── sample_email.json        # Sample input for testing
├── run.sh                   # Helper script to run the service
├── PRD.md                   # Product Requirements Document
└── README.md                # This file
```

## Installation

### 1. Create Virtual Environment

```bash
python3 -m venv venv
```

### 2. Install Dependencies

```bash
./venv/bin/pip install -r requirements.txt
```

## Usage

### Standalone Execution

Using the helper script (recommended):

```bash
./run.sh --input sample_email.json
```

Or directly:

```bash
PYTHONPATH=. ./venv/bin/python __main__.py --input sample_email.json
```

### Command-line Options

```bash
./run.sh --input <input_file> [--config <config_file>] [--output <output_file>]
```

- `--input`: Path to input JSON file (required)
- `--config`: Path to configuration file (default: config.yaml)
- `--output`: Path to output JSON file (optional, prints to stdout if not specified)

### Input Format

```json
{
  "raw_email": {
    "message_id": "msg_12345abc",
    "thread_id": "thread_67890def",
    "sender": "student@example.com",
    "subject": "Self check of homework 42",
    "body": "Repository: https://github.com/student123/homework-42",
    "datetime": "2026-01-11T10:30:00Z"
  }
}
```

### Output Format

```json
{
  "email_id": "7dec440a1ccf87c09668e4a563e8fc2e28ab00dc6e6bc7707338e8dabeb49062",
  "message_id": "msg_12345abc",
  "email_datetime": "2026-01-11T10:30:00Z",
  "email_subject": "Self check of homework 42",
  "repo_url": "https://github.com/student123/homework-42",
  "sender_email": "student@example.com",
  "hashed_email": "616bb35d31d0a6840d2d5adfeacde5979ea99a18ab5fa7bb633460029e20717e",
  "thread_id": "thread_67890def",
  "status": "Ready",
  "missing_fields": []
}
```

## Testing

### Run All Tests

```bash
./venv/bin/python -m pytest tests/ -v
```

### Run Tests with Coverage

```bash
./venv/bin/python -m pytest tests/ -v --cov=src --cov-report=html
```

### Test Results

The test suite includes 28 comprehensive tests covering:
- Parser initialization and configuration
- Hash generation (email ID and sender email)
- GitHub URL extraction (multiple formats)
- Subject validation (pattern matching)
- Field validation (required fields)
- Complete email parsing workflow
- Edge cases and error handling

All tests pass successfully.

## Configuration

The service is configured via `config.yaml`:

```yaml
service:
  name: email_parser
  version: "1.0.0"

patterns:
  subject_pattern: "self check of homework \\d{1,3}"
  github_patterns:
    - "https://github.com/[\\w-]+/[\\w-]+(?:\\.git)?"
    - "github.com/[\\w-]+/[\\w-]+"

validation:
  required_fields:
    - repo_url
    - sender_email

logging:
  level: INFO
  file: "./logs/email_parser.log"
```

## Parsing Rules

### Email ID Generation

```python
email_id = sha256(f"{sender}:{subject}:{datetime}")
```

### GitHub URL Patterns

Supported formats:
- `https://github.com/username/repo-name.git`
- `https://github.com/username/repo-name`
- `github.com/username/repo-name`

All URLs are normalized to `https://github.com/username/repo-name` format.

### Subject Validation

Expected pattern: `self check of homework \d{1,3}` (case-insensitive)

Examples:
- "Self check of homework 1" ✓
- "self check of homework 42" ✓
- "SELF CHECK OF HOMEWORK 100" ✓
- "Random subject" ✗

### Status Determination

- **Ready**: All required fields (repo_url, sender_email) are present
- **Missing: [fields]**: Lists missing required fields

## Dependencies

### Python Packages
- `pyyaml>=6.0` - Configuration file parsing
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Test coverage

### Shared Utilities (Referenced in PRD)
- `shared.utils.hash_utils`
- `shared.utils.validators`
- `shared.models.email_data`
- `shared.interfaces.service_interface`

## Parent Service

This service is designed to be called by the **Email Reader** service located at `../`.

## API Integration

As a leaf service, this parser has **no external API dependencies**. It performs internal logic only.

## Exit Codes

- `0`: Email parsed successfully (status: "Ready")
- `1`: Error during processing
- `2`: Email parsed but has missing fields

## Logs

Logs are written to `./logs/email_parser.log` with the following information:
- Service initialization
- Email parsing operations
- GitHub URL extraction results
- Subject validation warnings
- Missing field warnings
- Successful parsing confirmations

## Version

Current version: **1.0.0**

## License

Part of the L30 Homework Orchestrator system.

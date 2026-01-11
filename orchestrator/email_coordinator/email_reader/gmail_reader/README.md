# Gmail Reader Service

A leaf service that reads emails from Gmail API matching homework submission patterns.

## Overview

**Level:** 3 (Leaf Service)
**Parent:** Email Reader (`../`)
**External API:** Gmail API (read and modify scopes)

This service authenticates with Gmail API using OAuth2, searches for emails matching specified patterns, and returns structured email data to its parent service.

## Features

- OAuth2 authentication with Gmail API
- Search emails using Gmail query syntax
- Parse email metadata (sender, subject, datetime, etc.)
- Extract email body (text/plain and text/html)
- Mark emails as read after fetching (optional)
- Automatic token refresh
- Comprehensive logging

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Gmail API credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials and save as `./data/credentials/credentials.json`

## Configuration

Edit `config.yaml` to customize settings:

```yaml
gmail:
  credentials_path: "./data/credentials/credentials.json"
  token_path: "./data/credentials/token.json"
  scopes:
    - "https://www.googleapis.com/auth/gmail.readonly"
    - "https://www.googleapis.com/auth/gmail.modify"

defaults:
  max_results: 100
  search_query: "subject:(self check of homework) is:unread"
```

## Usage

### As a Module

```python
from service import GmailReaderService

# Initialize service
service = GmailReaderService(config_path="config.yaml")

# Read emails
input_data = {
    "search_query": "subject:(self check of homework) is:unread",
    "max_results": 10,
    "mark_as_read": False
}

result = service.process(input_data)

# Access results
if result['status'] == 'success':
    for email in result['emails']:
        print(f"From: {email['sender']}")
        print(f"Subject: {email['subject']}")
        print(f"Body: {email['body']}")
```

### Standalone Execution

```bash
# Use defaults from config
python -m gmail_reader

# Custom search query
python -m gmail_reader --search-query "subject:(homework) is:unread"

# Limit results
python -m gmail_reader --max-results 5

# Mark as read after fetching
python -m gmail_reader --mark-as-read
```

## Input Specification

```python
{
    "search_query": str,        # Gmail search query
    "max_results": int,         # Maximum emails to fetch
    "mark_as_read": bool        # Whether to mark as read after fetch
}
```

## Output Specification

```python
{
    "emails": List[{
        "message_id": str,      # Gmail message ID
        "thread_id": str,       # Gmail thread ID
        "sender": str,          # From header
        "subject": str,         # Subject header
        "body": str,            # Email body (decoded)
        "datetime": str,        # ISO format timestamp
        "snippet": str          # Email snippet
    }],
    "count": int,               # Number of emails
    "status": str               # "success" | "failed"
}
```

## Gmail Search Query Examples

```
# Default pattern
subject:(self check of homework) is:unread

# Specific homework number
subject:(self check of homework 5) is:unread

# From specific sender
from:student@example.com subject:(homework)

# Date range
after:2024/01/01 before:2024/12/31 subject:(homework)

# Has attachment
has:attachment subject:(homework)
```

## Authentication Flow

1. **First Run:** Opens browser for OAuth consent
2. **Token Storage:** Saves token to `./data/credentials/token.json`
3. **Subsequent Runs:** Uses saved token automatically
4. **Token Refresh:** Auto-refreshes when expired

## Testing

Run tests with pytest:

```bash
cd orchestrator/email_coordinator/email_reader/gmail_reader
python -m pytest tests/ -v
```

Run specific test:

```bash
pytest tests/test_service.py::TestGmailReaderService::test_process_success -v
```

## Directory Structure

```
gmail_reader/
├── __init__.py
├── __main__.py
├── service.py
├── config.yaml
├── requirements.txt
├── README.md
├── PRD.md
├── data/
│   └── credentials/
│       ├── credentials.json    # OAuth client credentials (not in git)
│       └── token.json          # Generated token (not in git)
├── logs/
│   └── gmail_reader.log        # Service logs (not in git)
└── tests/
    ├── __init__.py
    └── test_service.py
```

## Logging

Logs are written to both file and console:
- **File:** `./logs/gmail_reader.log`
- **Level:** INFO (configurable in `config.yaml`)
- **Format:** `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Error Handling

The service handles:
- Gmail API HTTP errors
- Authentication failures
- Token expiration and refresh
- Missing or invalid credentials
- Network errors
- Malformed email messages

All errors are logged and return `status: "failed"` with empty results.

## Dependencies

- `google-api-python-client` - Gmail API client
- `google-auth-httplib2` - HTTP library for authentication
- `google-auth-oauthlib` - OAuth2 flow
- `pyyaml` - YAML configuration parsing
- `pytest` - Testing framework

## Notes

- First run requires browser access for OAuth consent
- Credentials and tokens are stored locally (not committed to git)
- The service supports both simple and multipart email formats
- HTML emails are decoded but not rendered
- Email body extraction prefers plain text over HTML

## Troubleshooting

**Issue:** "credentials.json not found"
- Download OAuth credentials from Google Cloud Console
- Place in `./data/credentials/credentials.json`

**Issue:** "Invalid grant" error
- Delete `./data/credentials/token.json`
- Re-run to re-authenticate

**Issue:** "Insufficient permissions"
- Check OAuth scopes in config.yaml
- Re-authenticate to grant new permissions

## License

Part of the L30 Homework Processing System.

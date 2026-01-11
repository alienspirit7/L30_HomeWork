# Draft Composer Service

A leaf service that creates and saves email drafts in Gmail as replies to original emails.

## Overview

- **Level**: 3 (Leaf Service)
- **Parent**: Draft Manager
- **External API**: Gmail API (compose scope)

## Features

- Creates Gmail drafts as threaded replies
- Maintains email thread continuity using In-Reply-To headers
- OAuth2 authentication with Gmail API
- Configurable via YAML
- Supports both programmatic and CLI usage

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials and save as `./data/credentials/credentials.json`

### 3. Directory Structure

```
draft_composer/
├── config.yaml
├── requirements.txt
├── service.py
├── __init__.py
├── README.md
├── data/
│   └── credentials/
│       ├── credentials.json   # Your OAuth credentials (not committed)
│       └── token.json          # Auto-generated after first auth
├── logs/
│   └── draft_composer.log     # Service logs
└── tests/
    ├── __init__.py
    └── test_service.py
```

## Usage

### Programmatic Usage

```python
from draft_composer import DraftComposerService

# Initialize service
service = DraftComposerService(config_path="./config.yaml")

# Create draft
input_data = {
    "to_email": "student@example.com",
    "subject": "Re: Homework Question",
    "body": "Great work on your assignment!",
    "thread_id": "thread_abc123",
    "in_reply_to": "<msg_xyz789@mail.gmail.com>"
}

result = service.process(input_data)
print(f"Draft ID: {result['draft_id']}")
print(f"Status: {result['status']}")
```

### Command Line Usage

```bash
python -m service \
    --to "student@example.com" \
    --subject "Re: Homework Question" \
    --body "Great work!" \
    --thread-id "thread_abc123" \
    --in-reply-to "<msg_xyz789@mail.gmail.com>"
```

## Input Specification

```python
{
    "to_email": str,       # Recipient email address
    "subject": str,        # Email subject line
    "body": str,          # Email body content
    "thread_id": str,     # Gmail thread ID for proper threading
    "in_reply_to": str    # Original message ID for In-Reply-To header
}
```

## Output Specification

```python
{
    "draft_id": str,      # Gmail draft ID (None if failed)
    "status": str,        # "Created" | "Failed"
    "error": str | None   # Error message if failed
}
```

## Configuration

Edit `config.yaml` to customize:

```yaml
service:
  name: draft_composer
  version: "1.0.0"

gmail:
  credentials_path: "./data/credentials/credentials.json"
  token_path: "./data/credentials/token.json"
  scopes:
    - "https://www.googleapis.com/auth/gmail.compose"

defaults:
  sender_name: "Elena"
  subject_prefix: "Re: "

logging:
  level: INFO
  file: "./logs/draft_composer.log"
```

## Testing

Run the test suite:

```bash
cd orchestrator/email_coordinator/draft_manager/draft_composer
python -m pytest tests/ -v
```

Or using unittest:

```bash
python -m unittest discover tests/
```

## Authentication Flow

On first run:
1. Service will open browser for Google OAuth consent
2. Sign in with your Google account
3. Grant Gmail compose permissions
4. Token will be saved to `./data/credentials/token.json`
5. Subsequent runs will use the saved token

## Error Handling

The service handles:
- Missing required input fields
- Gmail API authentication errors
- Network connectivity issues
- Invalid thread or message IDs
- Insufficient permissions

All errors are logged and returned in the output with status "Failed".

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- The service only requests `gmail.compose` scope (minimal permissions)
- Drafts are not automatically sent - teacher must manually review and send

## Integration

This service is designed to be called by the Draft Manager parent service but can also run standalone for testing and development.

### Parent Service Integration

```python
# In Draft Manager
from draft_composer import DraftComposerService

composer = DraftComposerService()
result = composer.process(draft_data)
```

## Logs

Service logs are written to `./logs/draft_composer.log` and include:
- Authentication events
- Draft creation requests
- Success/failure status
- Error details

## Dependencies

- `google-api-python-client>=2.0.0` - Gmail API client
- `google-auth-httplib2>=0.1.0` - HTTP library for Google Auth
- `google-auth-oauthlib>=1.0.0` - OAuth2 flow implementation
- `pyyaml>=6.0.0` - YAML configuration parsing

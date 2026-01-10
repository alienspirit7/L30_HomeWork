# Gmail Reader Service PRD (Level 3 - Leaf 1)

## Purpose
Reads emails from Gmail API matching homework submission pattern. This is a **leaf service** with **external API access**.

## Level
3 (Leaf Service)

## Parent
| Parent | Path |
|--------|------|
| Email Reader | `../` |

## Children
None (Leaf node)

## External API
**Gmail API** (read scope)

---

## Input Specification

**From Parent (Email Reader):**
```python
{
    "search_query": str,        # Gmail search query
    "max_results": int,         # Maximum emails to fetch
    "mark_as_read": bool        # Whether to mark as read after fetch
}
```

## Output Specification

**To Parent (Email Reader):**
```python
{
    "emails": List[{
        "message_id": str,
        "thread_id": str,
        "sender": str,
        "subject": str,
        "body": str,
        "datetime": str,
        "snippet": str
    }],
    "count": int,
    "status": str               # "success" | "failed"
}
```

---

## Configuration

`config.yaml`:
```yaml
service:
  name: gmail_reader
  version: "1.0.0"

gmail:
  credentials_path: "./data/credentials/credentials.json"
  token_path: "./data/credentials/token.json"
  scopes:
    - "https://www.googleapis.com/auth/gmail.readonly"
    - "https://www.googleapis.com/auth/gmail.modify"

defaults:
  max_results: 100
  search_query: "subject:(self check of homework) is:unread"

logging:
  level: INFO
  file: "./logs/gmail_reader.log"
```

`requirements.txt`:
```
google-api-python-client>=2.0.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=1.0.0
```

---

## Gmail Search Query

Default pattern:
```
subject:(self check of homework) is:unread
```

Matches:
- "Self Check of Homework 5" ✓
- "SELF CHECK OF HOMEWORK 42" ✓
- "self check of homework 123" ✓

---

## Authentication Flow

1. First run: Opens browser for OAuth consent
2. Saves token to `./data/credentials/token.json`
3. Subsequent runs: Uses saved token
4. Token refresh: Automatic when expired

---

## Data Directory

```
./data/
└── credentials/
    ├── credentials.json    # OAuth client credentials
    └── token.json          # Generated OAuth token
```

---

## Dependencies
- `shared.interfaces.service_interface`
- `shared.utils.logger`

---

## Testing
```bash
cd orchestrator/email_coordinator/email_reader/gmail_reader
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/email_coordinator/email_reader/gmail_reader
python -m service --max-results 5
```

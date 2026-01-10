# Draft Composer Service PRD (Level 3 - Leaf 3)

## Purpose
Creates and saves email drafts in Gmail as replies to original emails. This is a **leaf service** with **external API access**.

## Level
3 (Leaf Service)

## Parent
| Parent | Path |
|--------|------|
| Draft Manager | `../` |

## Children
None (Leaf node)

## External API
**Gmail API** (compose scope)

---

## Input Specification

**From Parent (Draft Manager):**
```python
{
    "to_email": str,
    "subject": str,
    "body": str,
    "thread_id": str,           # For reply threading
    "in_reply_to": str          # Original message ID
}
```

## Output Specification

**To Parent (Draft Manager):**
```python
{
    "draft_id": str,
    "status": str,              # "Created" | "Failed"
    "error": str | None
}
```

---

## Draft Format

The draft is created as a **reply** to the original email thread:
- Uses `In-Reply-To` header for threading
- Does NOT auto-send (remains in Drafts folder)
- Teacher can review before sending

---

## Configuration

`config.yaml`:
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

`requirements.txt`:
```
google-api-python-client>=2.0.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=1.0.0
```

---

## Data Directory

```
./data/
└── credentials/
    ├── credentials.json    # OAuth client credentials (shared/symlink)
    └── token.json          # Generated OAuth token
```

---

## Dependencies
- `shared.interfaces.service_interface`
- `shared.utils.logger`

---

## Testing
```bash
cd orchestrator/email_coordinator/draft_manager/draft_composer
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/email_coordinator/draft_manager/draft_composer
python -m service --to "student@example.com" --subject "Re: Homework" --body "Great job!"
```

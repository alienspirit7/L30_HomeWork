# Email Parser Service PRD (Level 3 - Leaf 2)

## Purpose
Extracts structured data from raw email content. Parses subject, body, GitHub URLs, and validates required fields. This is a **leaf service** with **no external API** (internal logic only).

## Level
3 (Leaf Service)

## Parent
| Parent | Path |
|--------|------|
| Email Reader | `../` |

## Children
None (Leaf node)

## External API
None (Internal logic)

---

## Input Specification

**From Parent (Email Reader):**
```python
{
    "raw_email": {
        "message_id": str,
        "thread_id": str,
        "sender": str,
        "subject": str,
        "body": str,
        "datetime": str
    }
}
```

## Output Specification

**To Parent (Email Reader):**
```python
{
    "email_id": str,            # SHA-256 hash
    "email_datetime": str,
    "email_subject": str,
    "repo_url": str | None,
    "sender_email": str,
    "hashed_email": str,        # SHA-256 of sender
    "thread_id": str,
    "status": str,              # "Ready" or "Missing: [fields]"
    "missing_fields": List[str]
}
```

---

## Parsing Rules

### Email ID Generation
```python
email_id = sha256(f"{sender}:{subject}:{datetime}")
```

### GitHub URL Extraction
Patterns matched:
- `https://github.com/username/repo-name.git`
- `https://github.com/username/repo-name`
- `github.com/username/repo-name`

### Subject Validation
Pattern: `self check of homework \d{1,3}` (case-insensitive)

### Status Determination
- **Ready**: All required fields present
- **Missing: [fields]**: Lists missing required fields

---

## Configuration

`config.yaml`:
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

`requirements.txt`:
```
# Uses shared utilities only
```

---

## Dependencies
- `shared.utils.hash_utils`
- `shared.utils.validators`
- `shared.models.email_data`
- `shared.interfaces.service_interface`

---

## Testing
```bash
cd orchestrator/email_coordinator/email_reader/email_parser
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/email_coordinator/email_reader/email_parser
python -m service --input sample_email.json
```

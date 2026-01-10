# Email Reader Manager PRD (Level 2 - Branch A1)

## Purpose
Manages inbound email processing: fetching emails from Gmail and parsing them into structured records.

## Level
2 (Task Manager)

## Parent
| Parent | Path |
|--------|------|
| Email Coordinator | `../` |

## Children
| Child | Path | Role |
|-------|------|------|
| Gmail Reader | `./gmail_reader/` | Fetches raw emails from Gmail API |
| Email Parser | `./email_parser/` | Extracts structured data from emails |

---

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
    "output_file": str,   # Path to file_1_2.xlsx
    "processed_count": int,
    "ready_count": int,   # Emails with status="Ready"
    "failed_count": int   # Emails with missing fields
}
```

**Data Output:**
`./data/output/file_1_2.xlsx`

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

---

## Workflow

1. Call `gmail_reader.execute(search_query, max_results)`
2. For each raw email:
   - Call `email_parser.execute(raw_email)`
   - Collect parsed EmailRecord
3. Write all records to `file_1_2.xlsx`
4. Return summary to parent

---

## Configuration

`config.yaml`:
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

`requirements.txt`:
```
openpyxl>=3.1.0
```

---

## Dependencies
- `shared.models.email_data`
- `shared.utils.file_utils`
- `shared.interfaces.coordinator_interface`
- `gmail_reader`
- `email_parser`

---

## Testing
```bash
cd orchestrator/email_coordinator/email_reader
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/email_coordinator/email_reader
python -m manager --mode test
```

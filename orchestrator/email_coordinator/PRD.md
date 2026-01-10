# Email Coordinator PRD (Level 1 - Branch A)

## Purpose
Coordinates all email-related operations: inbound email processing and outbound draft creation.

## Level
1 (Domain Coordinator)

## Parent
| Parent | Path |
|--------|------|
| Orchestrator | `../` |

## Children
| Child | Path | Role |
|-------|------|------|
| Email Reader | `./email_reader/` | Reads & parses incoming emails |
| Draft Manager | `./draft_manager/` | Creates outbound email drafts |

---

## Input Specification

**From Parent (Orchestrator):**
```python
{
    "action": str,        # "read_emails" | "create_drafts" | "full_pipeline"
    "mode": str,          # "test" | "batch" | "full"
    "batch_size": int,    # Number of emails to process
    "feedback_data": List[FeedbackRecord]  # For draft creation
}
```

## Output Specification

**To Parent (Orchestrator):**
```python
{
    "action": str,
    "status": str,        # "success" | "partial" | "failed"
    "emails_processed": int,
    "drafts_created": int,
    "errors": List[str]
}
```

---

## Workflow

### Action: read_emails
1. Call `email_reader.execute(mode, batch_size)`
2. Return parsed email records
3. Save to `email_reader/data/output/file_1_2.xlsx`

### Action: create_drafts
1. Load feedback data from `feedback_manager/data/output/file_3_4.xlsx`
2. Call `draft_manager.execute(email_records, feedback_records)`
3. Return draft creation results

### Action: full_pipeline
1. Execute read_emails
2. Wait for processing_coordinator to complete
3. Execute create_drafts

---

## Configuration

`config.yaml`:
```yaml
coordinator:
  name: email_coordinator
  version: "1.0.0"

children:
  email_reader: "./email_reader"
  draft_manager: "./draft_manager"

logging:
  level: INFO
  file: "./logs/email_coordinator.log"
```

`requirements.txt`:
```
# Inherits from shared
```

---

## Dependencies
- `shared.models.email_data`
- `shared.models.feedback_data`
- `shared.interfaces.coordinator_interface`
- `email_reader`
- `draft_manager`

---

## Testing
```bash
cd orchestrator/email_coordinator
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/email_coordinator
python -m coordinator --action read_emails --mode test
```

# Draft Manager PRD (Level 2 - Branch A2)

## Purpose
Manages outbound email draft creation: composing personalized drafts with student names and feedback.

## Level
2 (Task Manager)

## Parent
| Parent | Path |
|--------|------|
| Email Coordinator | `../` |

## Children
| Child | Path | Role |
|-------|------|------|
| Draft Composer | `./draft_composer/` | Creates drafts via Gmail API |
| Student Mapper | `./student_mapper/` | Maps emails to student names |

---

## Input Specification

**From Parent (Email Coordinator):**
```python
{
    "email_records": List[EmailRecord],   # From email_reader
    "feedback_records": List[FeedbackRecord]  # From feedback_manager
}
```

## Output Specification

**To Parent (Email Coordinator):**
```python
{
    "drafts_created": int,
    "drafts_failed": int,
    "draft_details": List[{
        "email_id": str,
        "draft_id": str,
        "status": str,
        "error": str | None
    }]
}
```

---

## Workflow

1. Load email records and feedback records
2. For each feedback record with status="Ready":
   - Find matching email record
   - Call `student_mapper.execute(sender_email)` → get student name
   - Compose email body:
     ```
     Hi, {name}!
     
     {feedback}
     
     Your code repository reviewed: {repo_url}
     
     Thanks, Elena
     ```
   - Call `draft_composer.execute(to_email, subject, body, thread_id)`
3. Return summary to parent

---

## Configuration

`config.yaml`:
```yaml
manager:
  name: draft_manager
  version: "1.0.0"

children:
  draft_composer: "./draft_composer"
  student_mapper: "./student_mapper"

email_template:
  greeting: "Hi, {name}!"
  signature: "Thanks, Elena"
  repo_line: "Your code repository reviewed: {repo_url}"

logging:
  level: INFO
  file: "./logs/draft_manager.log"
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
- `draft_composer`
- `student_mapper`

---

## Testing
```bash
cd orchestrator/email_coordinator/draft_manager
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/email_coordinator/draft_manager
python -m manager --email-file ../email_reader/data/output/file_1_2.xlsx \
                  --feedback-file ../../processing_coordinator/feedback_manager/data/output/file_3_4.xlsx
```

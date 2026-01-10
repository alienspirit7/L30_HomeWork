# Orchestrator PRD (Level 0 - Root)

## Purpose
Root coordinator and entry point for the Homework Grading System. Orchestrates the complete workflow by delegating to Level 1 coordinators.

## Level
0 (Root)

## Parent
None (This is the root)

## Children
| Child | Path | Role |
|-------|------|------|
| Email Coordinator | `./email_coordinator/` | Handles email processing & draft creation |
| Processing Coordinator | `./processing_coordinator/` | Handles grading & feedback generation |

---

## Input Specification
**CLI Arguments:**
```python
{
    "mode": str,          # "test" | "batch" | "full"
    "batch_size": int,    # 1-100 (for batch mode)
    "step": str           # "all" | "1" | "2" | "3" | "4"
}
```

## Output Specification
**Console Output:**
- Step-by-step progress
- Summary statistics
- Error reports

---

## Workflow

```
Step 1: Email Search     → email_coordinator.email_reader
Step 2: Clone & Grade    → processing_coordinator.grade_manager
Step 3: Generate Feedback → processing_coordinator.feedback_manager
Step 4: Create Drafts    → email_coordinator.draft_manager
```

### Data Passing Strategy

Data flows between coordinators via **in-memory objects**, not file paths:

```python
# Step 1: Get emails
email_result = email_coordinator.read_emails(mode, batch_size)
email_records = email_result["emails"]

# Step 2: Grade (pass email_records)
grade_result = processing_coordinator.grade(email_records)
grade_records = grade_result["grades"]

# Step 3: Feedback (pass grade_records)
feedback_result = processing_coordinator.generate_feedback(grade_records)
feedback_records = feedback_result["feedback"]

# Step 4: Drafts (pass both email_records and feedback_records)
draft_result = email_coordinator.create_drafts(email_records, feedback_records)
```

Each manager also saves its output to Excel files for persistence/recovery.

---

## Configuration

`config.yaml`:
```yaml
orchestrator:
  name: homework_grading_orchestrator
  version: "1.0.0"

modes:
  test:
    batch_size: 1
  batch:
    max_batch_size: 100
    default_batch_size: 10
  full:
    process_all: true

children:
  email_coordinator: "./email_coordinator"
  processing_coordinator: "./processing_coordinator"

logging:
  level: INFO
  file: "./logs/orchestrator.log"
```

`requirements.txt`:
```
click>=8.0.0
rich>=13.0.0
```

---

## CLI Menu Structure

```
=== Homework Grading System ===

Mode Selection:
1. Test Mode (1 email)
2. Batch Mode (N emails)
3. Full Mode (all unread)
4. Exit

Main Menu:
1. Search Emails (Step 1)
2. Clone & Grade (Step 2)
3. Generate Feedback (Step 3)
4. Create Drafts (Step 4)
5. Run All Steps
6. Reset
7. Change Mode
8. Exit
```

---

## Dependencies
- `shared.utils.logger`
- `shared.config.base_config`
- `email_coordinator`
- `processing_coordinator`

---

## Testing
```bash
cd orchestrator
python -m pytest tests/ -v
```

## Run
```bash
cd orchestrator
python main.py
```

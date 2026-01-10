# Processing Coordinator PRD (Level 1 - Branch B)

## Purpose
Coordinates repository processing operations: cloning/grading repositories and generating AI feedback.

## Level
1 (Domain Coordinator)

## Parent
| Parent | Path |
|--------|------|
| Orchestrator | `../` |

## Children
| Child | Path | Role |
|-------|------|------|
| Grade Manager | `./grade_manager/` | Clones repos & calculates grades |
| Feedback Manager | `./feedback_manager/` | Generates AI feedback |

---

## Input Specification

**From Parent (Orchestrator):**
```python
{
    "action": str,        # "grade" | "feedback" | "full_pipeline"
    "email_records": List[EmailRecord]  # From email_reader
}
```

## Output Specification

**To Parent (Orchestrator):**
```python
{
    "action": str,
    "status": str,        # "success" | "partial" | "failed"
    "repos_graded": int,
    "feedback_generated": int,
    "errors": List[str]
}
```

---

## Workflow

### Action: grade
1. Load email records from `email_reader/data/output/file_1_2.xlsx`
2. Call `grade_manager.execute(email_records)`
3. Return grade results
4. Save to `grade_manager/data/output/file_2_3.xlsx`

### Action: feedback
1. Load grade records from `grade_manager/data/output/file_2_3.xlsx`
2. Call `feedback_manager.execute(grade_records)`
3. Return feedback results
4. Save to `feedback_manager/data/output/file_3_4.xlsx`

### Action: full_pipeline
1. Execute grade
2. Execute feedback

---

## Configuration

`config.yaml`:
```yaml
coordinator:
  name: processing_coordinator
  version: "1.0.0"

children:
  grade_manager: "./grade_manager"
  feedback_manager: "./feedback_manager"

logging:
  level: INFO
  file: "./logs/processing_coordinator.log"
```

`requirements.txt`:
```
# Inherits from shared
```

---

## Dependencies
- `shared.models.email_data`
- `shared.models.grade_data`
- `shared.models.feedback_data`
- `shared.interfaces.coordinator_interface`
- `grade_manager`
- `feedback_manager`

---

## Testing
```bash
cd orchestrator/processing_coordinator
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/processing_coordinator
python -m coordinator --action grade
python -m coordinator --action feedback
```

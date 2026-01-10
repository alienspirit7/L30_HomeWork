# Feedback Manager PRD (Level 2 - Branch B2)

## Purpose
Manages AI feedback generation: selecting feedback styles based on grades and generating personalized feedback using Gemini API.

## Level
2 (Task Manager)

## Parent
| Parent | Path |
|--------|------|
| Processing Coordinator | `../` |

## Children
| Child | Path | Role |
|-------|------|------|
| Gemini Generator | `./gemini_generator/` | Generates feedback via Gemini API |
| Style Selector | `./style_selector/` | Selects feedback style by grade |

---

## Input Specification

**From Parent (Processing Coordinator):**
```python
{
    "grade_records": List[GradeRecord]  # Only records with status="Ready"
}
```

## Output Specification

**To Parent (Processing Coordinator):**
```python
{
    "feedback": List[FeedbackRecord],
    "output_file": str,   # Path to file_3_4.xlsx
    "generated_count": int,
    "failed_count": int
}
```

**Data Output:**
`./data/output/file_3_4.xlsx`

| Column | Type | Description |
|--------|------|-------------|
| email_id | str | Matching email_id |
| reply | str | Generated feedback text (or None) |
| status | str | "Ready" or "Missing: reply" |

---

## Feedback Styles

| Grade Range | Style | Description |
|-------------|-------|-------------|
| 90-100 | Trump | Enthusiastic, superlatives |
| 70-89 | Hason | Witty, humorous |
| 55-69 | Constructive | Helpful, encouraging |
| 0-54 | Amsalem | Brash, confrontational |

---

## Workflow

1. Load grade records from `grade_manager/data/output/file_2_3.xlsx`
2. For each grade with status="Ready":
   - Call `style_selector.execute(grade)` → get style & prompt
   - Call `gemini_generator.execute(prompt, style, context)` → get feedback
   - Create FeedbackRecord
   - If API fails: set reply=None, status="Missing: reply"
3. Write all feedback to `file_3_4.xlsx`
4. Return summary to parent

---

## Configuration

`config.yaml`:
```yaml
manager:
  name: feedback_manager
  version: "1.0.0"

children:
  gemini_generator: "./gemini_generator"
  style_selector: "./style_selector"

output:
  file_path: "./data/output/file_3_4.xlsx"

rate_limiting:
  delay_between_calls_seconds: 60

logging:
  level: INFO
  file: "./logs/feedback_manager.log"
```

`requirements.txt`:
```
openpyxl>=3.1.0
```

---

## Error Handling

- **Gemini API failure**: Leave reply empty, set status="Missing: reply"
- **No fallback text**: Only genuine AI feedback proceeds
- **Retry on next run**: Failed records remain for reprocessing

---

## Dependencies
- `shared.models.grade_data`
- `shared.models.feedback_data`
- `shared.utils.file_utils`
- `shared.interfaces.coordinator_interface`
- `gemini_generator`
- `style_selector`

---

## Testing
```bash
cd orchestrator/processing_coordinator/feedback_manager
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/processing_coordinator/feedback_manager
python -m manager --input ../grade_manager/data/output/file_2_3.xlsx
```

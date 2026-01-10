# Style Selector Service PRD (Level 3 - Leaf 8)

## Purpose
Selects feedback style and prompt template based on student's grade. Returns the appropriate persona and prompt for the Gemini Generator. This is a **leaf service** with **no external API** (internal logic only).

## Level
3 (Leaf Service)

## Parent
| Parent | Path |
|--------|------|
| Feedback Manager | `../` |

## Children
None (Leaf node)

## External API
None (Internal logic)

---

## Input Specification

**From Parent (Feedback Manager):**
```python
{
    "grade": float              # 0-100
}
```

## Output Specification

**To Parent (Feedback Manager):**
```python
{
    "style_name": str,
    "style_description": str,
    "prompt_template": str
}
```

---

## Style Definitions

| Grade Range | Style Name | Description |
|-------------|------------|-------------|
| 90-100 | trump | Enthusiastic, uses superlatives, very positive |
| 70-89 | hason | Witty, humorous Israeli comedian style |
| 55-69 | constructive | Helpful, encouraging but honest feedback |
| 0-54 | amsalem | Brash, confrontational firebrand style |

---

## Configuration

`config.yaml`:
```yaml
service:
  name: style_selector
  version: "1.0.0"

styles:
  - name: "trump"
    grade_range: [90, 100]
    description: "Enthusiastic, uses superlatives like 'tremendous', 'fantastic', 'the best'"
    prompt: |
      Generate feedback in Donald Trump's enthusiastic style.
      Use phrases like "tremendous job", "fantastic work", "the best code I've ever seen".
      Be extremely positive and use lots of superlatives.
      Student grade: {grade}/100
      
  - name: "hason"
    grade_range: [70, 89]
    description: "Witty, humorous Israeli comedian style"
    prompt: |
      Generate feedback in Shahar Hason's witty Israeli comedian style.
      Be clever, use humor, make gentle jokes about coding.
      Praise the good work but keep it light and fun.
      Student grade: {grade}/100
      
  - name: "constructive"
    grade_range: [55, 69]
    description: "Helpful, encouraging but honest feedback"
    prompt: |
      Generate constructive feedback encouraging improvement.
      Acknowledge what was done well, but focus on areas for growth.
      Be supportive and provide specific suggestions.
      Student grade: {grade}/100
      
  - name: "amsalem"
    grade_range: [0, 54]
    description: "Brash, confrontational firebrand style"
    prompt: |
      Generate feedback in Dudi Amsalem's brash, confrontational style.
      Be direct and blunt about the issues with the code.
      Show disappointment but still push for improvement.
      Student grade: {grade}/100

logging:
  level: INFO
  file: "./logs/style_selector.log"
```

`requirements.txt`:
```
# Uses shared utilities only
```

---

## Selection Logic

```python
def select_style(grade: float) -> Style:
    if grade >= 90:
        return styles["trump"]
    elif grade >= 70:
        return styles["hason"]
    elif grade >= 55:
        return styles["constructive"]
    else:
        return styles["amsalem"]
```

---

## Dependencies
- `shared.interfaces.service_interface`
- `shared.config.base_config`

---

## Testing
```bash
cd orchestrator/processing_coordinator/feedback_manager/style_selector
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/processing_coordinator/feedback_manager/style_selector
python -m service --grade 85
```

# Python Analyzer Service PRD (Level 3 - Leaf 6)

## Purpose
Analyzes Python files in a repository and calculates a grade based on line count metrics. Files with >150 lines are considered well-structured. This is a **leaf service** with **file system access**.

## Level
3 (Leaf Service)

## Parent
| Parent | Path |
|--------|------|
| Grade Manager | `../` |

## Children
None (Leaf node)

## External API
File System (read)

---

## Input Specification

**From Parent (Grade Manager):**
```python
{
    "repository_path": str
}
```

## Output Specification

**To Parent (Grade Manager):**
```python
{
    "total_files": int,
    "total_lines": int,
    "lines_above_150": int,
    "grade": float,             # 0-100
    "file_details": List[{
        "filename": str,
        "line_count": int,
        "above_threshold": bool
    }],
    "status": str               # "Success" | "Failed"
}
```

---

## Grading Formula

```python
grade = (lines_in_files_above_150 / total_lines) * 100
```

Where:
- `lines_in_files_above_150`: Sum of lines from files with >150 lines
- `total_lines`: Sum of lines from ALL Python files

---

## Line Counting Rules

**Counted:**
- Code lines

**Excluded:**
- Blank lines (empty or whitespace only)
- Comment lines (starting with `#`)
- Docstrings (triple-quoted strings)

---

## File Exclusions

| Pattern | Reason |
|---------|--------|
| `**/venv/**` | Virtual environment |
| `**/__pycache__/**` | Compiled Python |
| `**/test_*.py` | Test files |
| `**/*_test.py` | Test files |
| `**/setup.py` | Package setup |
| `**/conftest.py` | Pytest config |

---

## Configuration

`config.yaml`:
```yaml
service:
  name: python_analyzer
  version: "1.0.0"

analysis:
  file_extensions: [".py"]
  exclude_patterns:
    - "**/venv/**"
    - "**/__pycache__/**"
    - "**/test_*.py"
    - "**/*_test.py"
    - "**/setup.py"
    - "**/conftest.py"

grading:
  line_threshold: 150
  exclude_comments: true
  exclude_blank_lines: true
  exclude_docstrings: true

logging:
  level: INFO
  file: "./logs/python_analyzer.log"
```

`requirements.txt`:
```
# Uses standard library only
```

---

## Dependencies
- `shared.models.grade_data`
- `shared.interfaces.service_interface`
- `shared.utils.logger`

---

## Testing
```bash
cd orchestrator/processing_coordinator/grade_manager/python_analyzer
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/processing_coordinator/grade_manager/python_analyzer
python -m service --path /path/to/repository
```

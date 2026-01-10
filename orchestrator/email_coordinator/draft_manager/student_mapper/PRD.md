# Student Mapper Service PRD (Level 3 - Leaf 4)

## Purpose
Maps email addresses to student names using a lookup table (Excel file). This is a **leaf service** with **file system access**.

## Level
3 (Leaf Service)

## Parent
| Parent | Path |
|--------|------|
| Draft Manager | `../` |

## Children
None (Leaf node)

## External API
File System (Excel read)

---

## Input Specification

**From Parent (Draft Manager):**
```python
{
    "email_address": str
}
```

## Output Specification

**To Parent (Draft Manager):**
```python
{
    "name": str | None,
    "found": bool
}
```

---

## Data File

**Location:** `./data/students_mapping.xlsx`

**Structure:**

| email_address | name |
|---------------|------|
| student1@example.com | Alex Johnson |
| student2@example.com | Maria Garcia |

---

## Configuration

`config.yaml`:
```yaml
service:
  name: student_mapper
  version: "1.0.0"

data:
  mapping_file: "./data/students_mapping.xlsx"
  
columns:
  email_column: "email_address"
  name_column: "name"

defaults:
  fallback_name: "Student"

caching:
  enabled: true
  reload_on_change: true

logging:
  level: INFO
  file: "./logs/student_mapper.log"
```

`requirements.txt`:
```
openpyxl>=3.1.0
```

---

## Lookup Behavior

1. Load mapping file on startup
2. Cache in memory for performance
3. Case-insensitive email matching
4. Return fallback name if not found

---

## Data Directory

```
./data/
└── students_mapping.xlsx
```

---

## Dependencies
- `shared.utils.file_utils`
- `shared.models.student_data`
- `shared.interfaces.service_interface`

---

## Testing
```bash
cd orchestrator/email_coordinator/draft_manager/student_mapper
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/email_coordinator/draft_manager/student_mapper
python -m service --email "student@example.com"
```

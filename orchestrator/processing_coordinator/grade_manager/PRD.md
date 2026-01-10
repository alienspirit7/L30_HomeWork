# Grade Manager PRD (Level 2 - Branch B1)

## Purpose
Manages repository grading: cloning GitHub repositories and analyzing Python code to calculate grades.

## Level
2 (Task Manager)

## Parent
| Parent | Path |
|--------|------|
| Processing Coordinator | `../` |

## Children
| Child | Path | Role |
|-------|------|------|
| GitHub Cloner | `./github_cloner/` | Clones repositories from GitHub |
| Python Analyzer | `./python_analyzer/` | Analyzes Python files for grading |

---

## Input Specification

**From Parent (Processing Coordinator):**
```python
{
    "email_records": List[EmailRecord]  # Only records with status="Ready"
}
```

## Output Specification

**To Parent (Processing Coordinator):**
```python
{
    "grades": List[GradeRecord],
    "output_file": str,   # Path to file_2_3.xlsx
    "graded_count": int,
    "failed_count": int
}
```

**Data Output:**
`./data/output/file_2_3.xlsx`

| Column | Type | Description |
|--------|------|-------------|
| email_id | str | Matching email_id from file_1_2.xlsx |
| grade | float | 0-100 calculated grade |
| status | str | "Ready" or "Failed" |

---

## Grading Formula

```
grade = (lines_in_files_above_150 / total_lines) × 100
```

- Only counts Python files (.py)
- Excludes comments and blank lines
- Excludes venv/, __pycache__/, test files

---

## Workflow

1. Load email records from `email_reader/data/output/file_1_2.xlsx`
2. For each email with status="Ready":
   - Call `github_cloner.execute(repo_url)` → get clone_path
   - Call `python_analyzer.execute(clone_path)` → get grade
   - Create GradeRecord
3. Write all grades to `file_2_3.xlsx`
4. Cleanup cloned repositories
5. Return summary to parent

---

## Configuration

`config.yaml`:
```yaml
manager:
  name: grade_manager
  version: "1.0.0"

children:
  github_cloner: "./github_cloner"
  python_analyzer: "./python_analyzer"

output:
  file_path: "./data/output/file_2_3.xlsx"

parallelism:
  max_workers: 5
  
cleanup:
  delete_repos_after_grading: true

logging:
  level: INFO
  file: "./logs/grade_manager.log"
```

`requirements.txt`:
```
openpyxl>=3.1.0
```

---

## Dependencies
- `shared.models.email_data`
- `shared.models.grade_data`
- `shared.utils.file_utils`
- `shared.interfaces.coordinator_interface`
- `github_cloner`
- `python_analyzer`

---

## Testing
```bash
cd orchestrator/processing_coordinator/grade_manager
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/processing_coordinator/grade_manager
python -m manager --input ../../email_coordinator/email_reader/data/output/file_1_2.xlsx
```

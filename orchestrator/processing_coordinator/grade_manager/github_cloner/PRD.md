# GitHub Cloner Service PRD (Level 3 - Leaf 5)

## Purpose
Clones Git repositories from GitHub to local filesystem. Supports parallel cloning with configurable timeout. This is a **leaf service** with **Git CLI access**.

## Level
3 (Leaf Service)

## Parent
| Parent | Path |
|--------|------|
| Grade Manager | `../` |

## Children
None (Leaf node)

## External API
**Git CLI** (command line)

---

## Input Specification

**From Parent (Grade Manager):**
```python
{
    "repo_url": str,
    "destination_dir": str,     # Optional, uses default if not provided
    "timeout_seconds": int      # Optional, defaults to 60
}
```

## Output Specification

**To Parent (Grade Manager):**
```python
{
    "clone_path": str,
    "status": str,              # "Success" | "Failed"
    "error": str | None,
    "duration_seconds": float
}
```

---

## Configuration

`config.yaml`:
```yaml
service:
  name: github_cloner
  version: "1.0.0"

git:
  command: "git"
  clone_args: ["--depth", "1"]  # Shallow clone for speed

defaults:
  timeout_seconds: 60
  temp_directory: "./data/tmp/repos"
  max_workers: 5

cleanup:
  delete_after_use: true

logging:
  level: INFO
  file: "./logs/github_cloner.log"
```

`requirements.txt`:
```
# Uses subprocess only (standard library)
```

---

## Supported URL Formats

- `https://github.com/username/repo-name.git`
- `https://github.com/username/repo-name`

---

## Cloning Strategy

1. **Shallow clone** (`--depth 1`) for speed
2. **Unique directory** per clone: `{temp_dir}/{email_id}/`
3. **Timeout protection** to handle hanging clones
4. **Cleanup** after grading is complete

---

## Data Directory

```
./data/
└── tmp/
    └── repos/
        ├── {email_id_1}/
        ├── {email_id_2}/
        └── ...
```

---

## Error Handling

| Error Type | Handling |
|------------|----------|
| Invalid URL | Return Failed + error message |
| Timeout | Kill process, return Failed |
| Private repo | Return Failed + "Access denied" |
| Network error | Return Failed + error details |

---

## Dependencies
- `shared.interfaces.service_interface`
- `shared.utils.logger`

---

## Testing
```bash
cd orchestrator/processing_coordinator/grade_manager/github_cloner
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/processing_coordinator/grade_manager/github_cloner
python -m service --url "https://github.com/user/repo"
```

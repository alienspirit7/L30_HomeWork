# Shared Module PRD

## Purpose
Centralized library of reusable components accessible by ALL modules in the binomial tree. Contains data models, utilities, interfaces, and configuration management.

## Level
N/A (Utility module, not part of tree hierarchy)

## Parent
None (Top-level utility)

## Dependencies
None (This is the base dependency)

---

## Components

### 1. Models (`models/`)
Shared data structures used across all modules.

| File | Classes | Used By |
|------|---------|---------|
| `email_data.py` | `EmailRecord`, `EmailStatus` | email_reader, draft_manager |
| `grade_data.py` | `GradeRecord`, `AnalysisResult` | grade_manager, feedback_manager |
| `feedback_data.py` | `FeedbackRecord`, `StyleType` | feedback_manager, draft_manager |
| `student_data.py` | `StudentRecord` | student_mapper, draft_manager |

### 2. Utils (`utils/`)
Common utility functions.

| File | Functions | Purpose |
|------|-----------|---------|
| `hash_utils.py` | `sha256_hash()`, `generate_id()` | ID generation, email hashing |
| `validators.py` | `validate_email()`, `validate_url()` | Input validation |
| `file_utils.py` | `read_excel()`, `write_excel()` | Excel I/O operations |
| `logger.py` | `get_logger()`, `LoggerConfig` | Logging configuration |

### 3. Interfaces (`interfaces/`)
Abstract base classes for consistent implementation.

| File | Classes | Implemented By |
|------|---------|----------------|
| `service_interface.py` | `ServiceInterface` | All Level 3 leaf services |
| `coordinator_interface.py` | `CoordinatorInterface` | Level 1 & 2 coordinators/managers |

### 4. Config (`config/`)
Configuration management.

| File | Classes | Purpose |
|------|---------|---------|
| `base_config.py` | `BaseConfig` | YAML config loading |
| `env_loader.py` | `load_env()` | Environment variable loading |

---

## Input Specification
N/A (Library module)

## Output Specification
N/A (Library module)

---

## Configuration
`requirements.txt`:
```
pyyaml>=6.0
python-dotenv>=1.0.0
openpyxl>=3.1.0
```

---

## Implementation Notes

1. **No circular dependencies**: Shared module must not import from any other module
2. **Type hints required**: All functions must have type annotations
3. **Docstrings required**: All public functions/classes must have docstrings
4. **Unit tests**: Each utility must have corresponding tests

---

## Testing
```bash
cd shared
python -m pytest tests/ -v
```

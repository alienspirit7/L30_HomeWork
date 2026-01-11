# Python Analyzer Service

A leaf service that analyzes Python files in a repository and calculates a grade based on line count metrics.

## Overview

This service:
- Scans Python repositories for `.py` files
- Counts lines of code (excluding comments, blank lines, and docstrings)
- Calculates a grade based on the proportion of lines in files with >150 lines
- Returns detailed analysis results

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Standalone Execution

```bash
python -m src --path /path/to/repository
```

### As a Module

```python
from src.service import PythonAnalyzerService

service = PythonAnalyzerService(config_path='config.yaml')
result = service.analyze('/path/to/repository')
print(result)
```

## Configuration

Edit `config.yaml` to customize:
- File extensions to analyze
- Exclusion patterns (venv, tests, etc.)
- Line threshold for grading (default: 150)
- Logging settings

## Grading Formula

```
grade = (lines_in_files_above_150 / total_lines) * 100
```

## Output Format

```json
{
    "total_files": 10,
    "total_lines": 1500,
    "lines_above_150": 900,
    "grade": 60.0,
    "file_details": [
        {
            "filename": "module.py",
            "line_count": 200,
            "above_threshold": true
        }
    ],
    "status": "Success"
}
```

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

## File Exclusions

The following patterns are excluded by default:
- `**/venv/**` - Virtual environments
- `**/__pycache__/**` - Compiled Python files
- `**/test_*.py` - Test files
- `**/*_test.py` - Test files
- `**/setup.py` - Setup files
- `**/conftest.py` - Pytest configuration

## Line Counting Rules

**Counted:**
- Code lines

**Excluded:**
- Blank lines (empty or whitespace only)
- Comment lines (starting with `#`)
- Docstrings (triple-quoted strings)

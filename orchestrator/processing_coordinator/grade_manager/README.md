# Grade Manager

A Level 2 task manager service that orchestrates the automated grading of student Python repositories. It clones GitHub repositories and analyzes Python code to calculate grades based on code structure metrics.

## Overview

Grade Manager is a coordinating service that:
- Reads student submission records from email processing pipeline
- Clones GitHub repositories using the GitHub Cloner service
- Analyzes Python code quality using the Python Analyzer service
- Calculates grades based on line count metrics
- Outputs results to Excel format for downstream processing

## Architecture

**Level:** 2 (Task Manager)

**Parent:** Processing Coordinator (`../`)

**Children:**
- **GitHub Cloner** (`./github_cloner/`) - Clones repositories from GitHub
- **Python Analyzer** (`./python_analyzer/`) - Analyzes Python files for grading

## Features

- Automated repository cloning and analysis workflow
- Parallel processing support (up to 5 concurrent operations)
- Comprehensive error handling and recovery
- Excel-based input/output for pipeline integration
- Automatic cleanup of temporary repositories
- Detailed logging and progress tracking
- Standalone execution mode for testing

## Installation

### Prerequisites
- Python 3.7+
- Git CLI installed and in PATH
- Excel input file from email_reader service

### Setup

1. **Clone or navigate to the grade_manager directory:**
```bash
cd orchestrator/processing_coordinator/grade_manager
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install child service dependencies:**
```bash
# GitHub Cloner
cd github_cloner
pip install -r requirements.txt
cd ..

# Python Analyzer
cd python_analyzer
pip install -r requirements.txt
cd ..
```

4. **Verify configuration:**
```bash
# Check that config.yaml exists and is properly configured
cat config.yaml
```

## Configuration

### config.yaml

```yaml
manager:
  name: grade_manager
  version: "1.0.0"

children:
  github_cloner: "./github_cloner"
  python_analyzer: "./python_analyzer"

input:
  # Path to email reader output
  file_path: "../email_coordinator/email_reader/data/output/file_1_2.xlsx"

output:
  # Path for grade results
  file_path: "./data/output/file_2_3.xlsx"

parallelism:
  # Maximum number of concurrent grading operations
  max_workers: 5

cleanup:
  # Delete cloned repositories after grading
  delete_repos_after_grading: true

logging:
  level: INFO
  file: "./logs/grade_manager.log"
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `manager.name` | `grade_manager` | Service identifier |
| `manager.version` | `1.0.0` | Service version |
| `children.github_cloner` | `./github_cloner` | Path to cloner service |
| `children.python_analyzer` | `./python_analyzer` | Path to analyzer service |
| `input.file_path` | Email reader output path | Input Excel file location |
| `output.file_path` | `./data/output/file_2_3.xlsx` | Output Excel file location |
| `parallelism.max_workers` | `5` | Max concurrent operations |
| `cleanup.delete_repos_after_grading` | `true` | Auto-delete cloned repos |
| `logging.level` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `logging.file` | `./logs/grade_manager.log` | Log file path |

## Usage

### Standalone Execution

**Basic usage (reads from default input path in config):**
```bash
python -m grade_manager
```

**With custom input file:**
```bash
python -m grade_manager --input ../../email_coordinator/email_reader/data/output/file_1_2.xlsx
```

**With custom output file:**
```bash
python -m grade_manager --input file_1_2.xlsx --output ./custom_output/grades.xlsx
```

**With custom config:**
```bash
python -m grade_manager --config custom_config.yaml
```

### Python API

```python
from grade_manager import GradeManagerService

# Initialize service
manager = GradeManagerService(config_path='config.yaml')

# Process email records
input_data = {
    'email_records': email_records  # List of EmailRecord objects
}

result = manager.process(input_data)

# Access results
print(f"Graded: {result['graded_count']}")
print(f"Failed: {result['failed_count']}")
print(f"Output file: {result['output_file']}")
```

### Integration with Parent Service

```python
# In Processing Coordinator
from grade_manager import GradeManagerService

manager = GradeManagerService()

# Pass filtered email records (status="Ready")
result = manager.process({
    'email_records': ready_records
})

# Result format:
# {
#     'grades': List[GradeRecord],
#     'output_file': './data/output/file_2_3.xlsx',
#     'graded_count': 15,
#     'failed_count': 2
# }
```

## Workflow

1. **Load Input**: Read email records from `file_1_2.xlsx` (only status="Ready")
2. **Clone Repository**: For each email record, clone the GitHub repository
3. **Analyze Code**: Run Python analyzer on cloned repository
4. **Calculate Grade**: Apply grading formula (lines in files >150 / total lines × 100)
5. **Record Results**: Create GradeRecord with email_id, grade, and status
6. **Cleanup**: Delete cloned repositories (if configured)
7. **Export Results**: Write all grades to `file_2_3.xlsx`
8. **Return Summary**: Report graded/failed counts to parent

## Input Specification

**Input File:** `file_1_2.xlsx` from email_reader service

**Required Columns:**
- `email_id` (str): Unique identifier
- `repo_url` (str): GitHub repository URL
- `status` (str): Must be "Ready" to be processed

**Example:**
```
email_id          | repo_url                                    | status
------------------|---------------------------------------------|--------
student001@uni.edu| https://github.com/student001/assignment-1 | Ready
student002@uni.edu| https://github.com/student002/assignment-1 | Ready
```

## Output Specification

**Output File:** `./data/output/file_2_3.xlsx`

**Columns:**
- `email_id` (str): Matching email_id from input
- `grade` (float): Calculated grade (0-100)
- `status` (str): "Ready" (success) or "Failed"

**Example:**
```
email_id          | grade | status
------------------|-------|--------
student001@uni.edu| 85.5  | Ready
student002@uni.edu| 72.3  | Ready
student003@uni.edu| 0.0   | Failed
```

## Grading Formula

```
grade = (lines_in_files_above_150 / total_lines) × 100
```

**Criteria:**
- Only counts Python files (.py)
- Excludes comments and blank lines
- Excludes docstrings
- Excludes test files, venv, __pycache__
- Files with >150 lines are considered well-structured

**Example:**
```
Repository has 3 files:
- main.py: 200 lines (above threshold)
- utils.py: 180 lines (above threshold)
- config.py: 50 lines (below threshold)

Total lines: 430
Lines in files >150: 380
Grade: (380 / 430) × 100 = 88.4
```

## Directory Structure

```
grade_manager/
├── README.md                  # This file
├── PRD.md                     # Product requirements document
├── config.yaml                # Main configuration file
├── requirements.txt           # Python dependencies
├── __init__.py               # Package initialization
├── __main__.py               # Module entry point
├── .gitignore                # Git ignore patterns
├── data/
│   └── output/
│       └── file_2_3.xlsx     # Grade results output
├── logs/
│   └── grade_manager.log     # Service logs
├── github_cloner/            # Child service: Repository cloner
│   ├── README.md
│   ├── PRD.md
│   ├── config.yaml
│   ├── requirements.txt
│   ├── service.py
│   ├── __init__.py
│   ├── __main__.py
│   ├── data/
│   │   └── tmp/
│   │       └── repos/        # Temporary clone directory
│   ├── logs/
│   └── tests/
└── python_analyzer/          # Child service: Code analyzer
    ├── README.md
    ├── PRD.md
    ├── config.yaml
    ├── requirements.txt
    ├── src/
    │   ├── service.py
    │   ├── file_analyzer.py
    │   ├── line_counter.py
    │   ├── grading_calculator.py
    │   ├── __init__.py
    │   └── __main__.py
    ├── logs/
    └── tests/
```

## Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Child Service Tests

```bash
# Test GitHub Cloner
cd github_cloner
python -m pytest tests/ -v
cd ..

# Test Python Analyzer
cd python_analyzer
python -m pytest tests/ -v
cd ..
```

### Integration Test

```bash
# Test the full workflow with sample data
python -m grade_manager --input tests/fixtures/sample_input.xlsx --output tests/output/test_grades.xlsx
```

## Error Handling

| Error Type | Handling | Status |
|------------|----------|--------|
| Invalid repository URL | Log error, set grade=0 | Failed |
| Clone timeout | Log error, set grade=0 | Failed |
| Private repository | Log error, set grade=0 | Failed |
| Network error | Log error, set grade=0 | Failed |
| Analysis failure | Log error, set grade=0 | Failed |
| No Python files found | Set grade=0 | Ready |
| Missing input file | Raise exception | - |
| Invalid input format | Raise exception | - |

## Logging

**Log file location:** `./logs/grade_manager.log`

**Log format:**
```
2026-01-11 10:30:45 - grade_manager - INFO - Starting grade manager v1.0.0
2026-01-11 10:30:46 - grade_manager - INFO - Loaded 20 email records
2026-01-11 10:30:47 - grade_manager - INFO - Processing student001@uni.edu
2026-01-11 10:30:50 - grade_manager - INFO - Grade calculated: 85.5
2026-01-11 10:31:15 - grade_manager - INFO - Grading complete: 18 graded, 2 failed
```

## Dependencies

**Core dependencies:**
- `openpyxl>=3.1.0` - Excel file reading/writing
- `pyyaml>=6.0` - YAML configuration parsing

**Child service dependencies:**
- GitHub Cloner: Git CLI, pyyaml, pytest
- Python Analyzer: pyyaml, pytest

## Performance

- **Parallel processing**: Grades up to 5 repositories concurrently
- **Shallow clones**: Uses `--depth 1` for faster cloning
- **Efficient analysis**: Streams file reading, no full repo loading
- **Typical timing**: 2-5 seconds per repository (varies by size)

## Limitations

- Only supports public GitHub repositories (or configured SSH access)
- Only analyzes Python (.py) files
- Requires Git CLI to be installed
- Excel format limited to ~1 million rows
- Parallel processing limited to avoid resource exhaustion

## Troubleshooting

### "Input file not found"
Ensure the email_reader service has run and generated `file_1_2.xlsx` in the correct location.

### "Git command not found"
Install Git and ensure it's available in system PATH:
```bash
git --version
```

### "Clone operation timed out"
Increase timeout in `github_cloner/config.yaml` or check network connection.

### "No Python files found"
Repository may not contain Python code. Grade will be 0 with status "Ready".

### "Module not found" errors
Install all dependencies for both main service and child services:
```bash
pip install -r requirements.txt
pip install -r github_cloner/requirements.txt
pip install -r python_analyzer/requirements.txt
```

### Permission errors when cleaning up
Ensure the service has write permissions to the `data/tmp/repos` directory.

## Child Services

### GitHub Cloner Service
Clones GitHub repositories with timeout protection and error handling.
- **Location:** `./github_cloner/`
- **Documentation:** [github_cloner/README.md](./github_cloner/README.md)

### Python Analyzer Service
Analyzes Python code and calculates grades based on line metrics.
- **Location:** `./python_analyzer/`
- **Documentation:** [python_analyzer/README.md](./python_analyzer/README.md)

## License

Part of the Processing Coordinator orchestrator system.

## Version

Current version: **1.0.0**

---

**Level:** 2 (Task Manager)
**Parent:** Processing Coordinator
**Children:** GitHub Cloner, Python Analyzer
**Input:** file_1_2.xlsx (email records)
**Output:** file_2_3.xlsx (grades)

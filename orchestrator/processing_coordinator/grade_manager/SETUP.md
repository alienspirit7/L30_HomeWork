# Grade Manager - Setup Guide

Quick setup guide for running the Grade Manager module as a standalone service.

## Prerequisites

- Python 3.7 or higher
- Git CLI installed and available in PATH
- pip (Python package manager)

## Installation Steps

### 1. Navigate to Grade Manager Directory

```bash
cd /path/to/orchestrator/processing_coordinator/grade_manager
```

### 2. Install Grade Manager Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `openpyxl` - For Excel file handling
- `pyyaml` - For YAML configuration parsing

### 3. Install GitHub Cloner Dependencies

```bash
cd github_cloner
pip install -r requirements.txt
cd ..
```

This installs:
- `pyyaml` - For YAML configuration
- `pytest` - For testing

### 4. Install Python Analyzer Dependencies

```bash
cd python_analyzer
pip install -r requirements.txt
cd ..
```

This installs:
- `PyYAML` - For YAML configuration

### 5. Verify Git Installation

```bash
git --version
```

Should output something like: `git version 2.x.x`

If not installed, install Git:
- **macOS:** `brew install git` or download from https://git-scm.com/
- **Linux:** `sudo apt-get install git` or `sudo yum install git`
- **Windows:** Download from https://git-scm.com/

## Configuration

### Main Configuration

Edit `config.yaml` to customize settings:

```yaml
manager:
  name: grade_manager
  version: "1.0.0"

children:
  github_cloner: "./github_cloner"
  python_analyzer: "./python_analyzer"

input:
  file_path: "../email_coordinator/email_reader/data/output/file_1_2.xlsx"

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

### Child Service Configurations

- **GitHub Cloner:** Edit `github_cloner/config.yaml` for clone settings
- **Python Analyzer:** Edit `python_analyzer/config.yaml` for analysis rules

## Verification

### Test GitHub Cloner

```bash
cd github_cloner
python3 service.py --url "https://github.com/octocat/Hello-World"
cd ..
```

Expected output:
```
============================================================
Clone Result:
============================================================
clone_path: /absolute/path/to/data/tmp/repos/Hello-World
status: Success
error: None
duration_seconds: 2.34
============================================================
```

### Test Python Analyzer

```bash
cd python_analyzer
python3 -m src --path ./src
cd ..
```

Expected output:
```
{
    "total_files": X,
    "total_lines": Y,
    "lines_above_150": Z,
    "grade": XX.X,
    "file_details": [...],
    "status": "Success"
}
```

### Test Grade Manager

```bash
python3 __main__.py --help
```

Expected output:
```
usage: __main__.py [-h] [--input INPUT] [--output OUTPUT] ...
```

## Running the Service

### Basic Execution

```bash
python3 __main__.py
```

### With Custom Input

```bash
python3 __main__.py --input /path/to/file_1_2.xlsx
```

### With Custom Output

```bash
python3 __main__.py --output /path/to/output.xlsx
```

## Directory Structure After Setup

```
grade_manager/
├── README.md                  # Main documentation
├── SETUP.md                   # This file
├── PRD.md                     # Product requirements
├── config.yaml                # Main configuration
├── requirements.txt           # Dependencies
├── __init__.py               # Package init
├── __main__.py               # Entry point
├── .gitignore                # Git ignore rules
├── data/
│   └── output/
│       ├── .gitkeep
│       └── file_2_3.xlsx     # Generated after run
├── logs/
│   ├── .gitkeep
│   └── grade_manager.log     # Generated after run
├── github_cloner/
│   ├── README.md
│   ├── config.yaml
│   ├── requirements.txt
│   ├── service.py
│   ├── data/tmp/repos/       # Temp clones
│   └── logs/
└── python_analyzer/
    ├── README.md
    ├── config.yaml
    ├── requirements.txt
    ├── src/
    └── logs/
```

## Troubleshooting

### Module Not Found Errors

Install all dependencies:
```bash
# Main service
pip install -r requirements.txt

# Child services
pip install -r github_cloner/requirements.txt
pip install -r python_analyzer/requirements.txt
```

### Git Command Not Found

Install Git CLI (see step 5 above).

### Permission Errors

Ensure write permissions for `data/` and `logs/` directories:
```bash
chmod -R u+w data/ logs/
```

### Missing Input File

Ensure the email_reader service has run first, or provide a custom input file path.

## Using Virtual Environments (Recommended)

For isolated Python environments:

```bash
# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
pip install -r github_cloner/requirements.txt
pip install -r python_analyzer/requirements.txt

# Run service
python __main__.py

# Deactivate when done
deactivate
```

## Next Steps

1. Ensure input file exists (from email_reader service)
2. Configure paths in `config.yaml`
3. Run tests (if available)
4. Execute the service
5. Check output file and logs

For detailed usage information, see [README.md](./README.md).

# Student Mapper Service

A leaf service that maps email addresses to student names using an Excel lookup table.

## Overview

- **Level**: 3 (Leaf Service)
- **Parent**: Draft Manager (`../`)
- **Version**: 1.0.0
- **External API**: File System (Excel read)

## Features

- Load student email-to-name mappings from Excel files
- In-memory caching for fast lookups
- Case-insensitive email matching
- Automatic fallback for unknown students
- Comprehensive logging
- Standalone CLI execution

## Installation

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

The service is configured via `config.yaml`:

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

## Data File Format

The Excel file (`./data/students_mapping.xlsx`) should have the following structure:

| email_address | name |
|---------------|------|
| student1@example.com | Alex Johnson |
| student2@example.com | Maria Garcia |

## Usage

### Standalone Execution

```bash
# Basic lookup
python -m src --email "student@example.com"

# JSON output
python -m src --email "student@example.com" --json

# Show statistics
python -m src --email "student@example.com" --stats

# Custom config file
python -m src --email "student@example.com" --config "./custom_config.yaml"
```

### As a Module

```python
from src.student_mapper import StudentMapper, lookup_student

# Using the class
mapper = StudentMapper("./config.yaml")
result = mapper.map_email_to_name("student@example.com")
print(result)  # {"name": "Alex Johnson", "found": True}

# Using the convenience function
result = lookup_student("student@example.com")
print(result)  # {"name": "Alex Johnson", "found": True}
```

### API Specification

#### Input

```python
{
    "email_address": str
}
```

#### Output

```python
{
    "name": str | None,
    "found": bool
}
```

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ -v --cov=src --cov-report=html
```

## Project Structure

```
student_mapper/
├── config.yaml              # Service configuration
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── PRD.md                  # Product Requirements Document
├── create_sample_data.py   # Script to generate sample data
├── data/
│   └── students_mapping.xlsx  # Student email-to-name mappings
├── src/
│   ├── __init__.py
│   ├── __main__.py         # Standalone execution entry point
│   └── student_mapper.py   # Main service implementation
├── tests/
│   ├── __init__.py
│   └── test_student_mapper.py  # Test suite
└── logs/
    └── student_mapper.log  # Service logs
```

## Logging

Logs are written to both the console and `./logs/student_mapper.log`. The log level can be configured in `config.yaml`.

Log format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Behavior

1. **Startup**: Loads mapping file into memory
2. **Caching**: All mappings are cached for fast lookups
3. **Matching**: Email addresses are matched case-insensitively
4. **Fallback**: Returns configured fallback name if email not found
5. **Reload**: Supports reloading mappings without restart

## Error Handling

- **Missing config file**: Raises `FileNotFoundError`
- **Missing data file**: Raises `FileNotFoundError`
- **Empty email**: Returns fallback name with `found: False`
- **Invalid email**: Returns fallback name with `found: False`

## Exit Codes (Standalone Mode)

- `0`: Student found successfully
- `1`: Student not found (fallback used)
- `2`: Configuration or data file not found
- `3`: Other errors

## Example Output

### Found Student

```
==================================================
Email: student1@example.com
Name: Alex Johnson
Found: Yes
==================================================
```

### Unknown Student

```
==================================================
Email: unknown@example.com
Name: Student
Found: No
==================================================
```

### JSON Format

```json
{
  "name": "Alex Johnson",
  "found": true
}
```

### Statistics

```json
{
  "total_mappings": 8,
  "service": "student_mapper",
  "version": "1.0.0"
}
```

## Dependencies

- `openpyxl>=3.1.0` - Excel file reading
- `pyyaml>=6.0` - YAML configuration parsing
- `pytest>=7.0.0` - Testing framework

## Integration with Parent Service

The Draft Manager service can call this service using:

```python
from student_mapper.src import lookup_student

# Simple lookup
result = lookup_student("student@example.com")

# Use the result
if result['found']:
    print(f"Dear {result['name']},")
else:
    print(f"Dear {result['name']},")  # Uses fallback
```

## Performance

- **Startup**: ~50ms (loads all mappings into memory)
- **Lookup**: <1ms (in-memory hash table lookup)
- **Memory**: ~1KB per 1000 student records

## Future Enhancements

- Support for CSV format
- Watch file for automatic reload
- Database backend option
- Multiple data sources
- Student metadata (e.g., ID, department)

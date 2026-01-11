# Style Selector Service

Level 3 - Leaf Service

## Overview

Selects feedback style and prompt template based on student's grade. Returns the appropriate persona and prompt for the Gemini Generator.

## Features

- **Four Distinct Styles**:
  - **Trump** (90-100): Enthusiastic, superlative-heavy feedback
  - **Hason** (70-89): Witty, humorous Israeli comedian style
  - **Constructive** (55-69): Helpful, encouraging improvement-focused
  - **Amsalem** (0-54): Brash, confrontational firebrand style

- **Internal Logic**: No external API calls, pure selection logic
- **Grade-Based Selection**: Automatic style selection based on grade ranges
- **Configurable**: YAML-based configuration for easy customization

## Installation

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### As a Module

```python
from service import StyleSelector

# Initialize service
selector = StyleSelector(config_path="config.yaml")

# Select style for a grade
result = selector.select_style(85.0)

# Or use the process method (parent service interface)
result = selector.process({"grade": 85.0})

# Result format:
# {
#     "style_name": "hason",
#     "style_description": "Witty, humorous Israeli comedian style",
#     "prompt_template": "Generate feedback in Shahar Hason's witty Israeli comedian style..."
# }
```

### Standalone Execution

```bash
# Activate virtual environment
source venv/bin/activate

# Run with specific grade
python -m service --grade 85

# Or
python service.py --grade 85
```

## Testing

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=service
```

## Input/Output Specification

### Input
```python
{
    "grade": float  # 0-100
}
```

### Output
```python
{
    "style_name": str,           # Name of selected style
    "style_description": str,    # Description of the style
    "prompt_template": str       # Formatted prompt for Gemini
}
```

## Style Ranges

| Grade Range | Style | Description |
|-------------|-------|-------------|
| 90-100 | trump | Enthusiastic, uses superlatives, very positive |
| 70-89 | hason | Witty, humorous Israeli comedian style |
| 55-69 | constructive | Helpful, encouraging but honest feedback |
| 0-54 | amsalem | Brash, confrontational firebrand style |

## Configuration

Edit `config.yaml` to customize:
- Service name and version
- Style definitions and grade ranges
- Prompt templates
- Logging settings

## Project Structure

```
style_selector/
├── config.yaml           # Configuration file
├── service.py           # Main service implementation
├── __init__.py          # Package initialization
├── __main__.py          # Module entry point
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── tests/              # Test suite
│   ├── __init__.py
│   └── test_service.py # Service tests (28 test cases)
├── logs/               # Log files directory
│   └── .gitkeep
└── venv/              # Virtual environment (not in git)
```

## Logging

Logs are written to:
- File: `./logs/style_selector.log`
- Console: stdout

Log level and file path can be configured in `config.yaml`.

## Dependencies

- Python 3.6+
- pyyaml>=6.0
- pytest>=7.4.0 (for testing)

## Parent Service

This service is called by the **Feedback Manager** service located at `../`.

## Version

1.0.0

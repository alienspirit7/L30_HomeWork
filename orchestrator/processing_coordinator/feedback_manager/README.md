# Feedback Manager

**Level 2 - Task Manager Service**

The Feedback Manager orchestrates the generation of personalized AI feedback for student assignments. It selects appropriate feedback styles based on grades and generates feedback using Google's Gemini API.

## Overview

This service manages the complete feedback generation workflow:
1. Loads graded student records from the Grade Manager
2. Selects feedback style based on grade ranges (Trump, Hason, Constructive, Amsalem)
3. Generates personalized AI feedback using Google Gemini API
4. Outputs feedback records with proper status tracking

## Features

- **Grade-Based Style Selection**: Automatically selects feedback tone based on performance
- **AI-Powered Generation**: Uses Google Gemini API for natural, personalized feedback
- **Rate Limiting**: Respects API quotas with configurable delays
- **Error Handling**: Graceful failure handling with retry logic
- **Status Tracking**: Clear status indicators for successful and failed generations
- **Standalone Execution**: Can run independently or as part of the orchestrator
- **Modular Architecture**: Two specialized child services handle specific tasks

## Architecture

```
feedback_manager/                    (Level 2 - Task Manager)
├── style_selector/                  (Level 3 - Internal Logic)
│   └── Selects feedback style by grade
└── gemini_generator/                (Level 3 - External API)
    └── Generates feedback via Gemini API
```

### Child Services

| Service | Path | Level | Purpose |
|---------|------|-------|---------|
| **Style Selector** | `./style_selector/` | 3 (Leaf) | Selects feedback style and prompt template based on grade |
| **Gemini Generator** | `./gemini_generator/` | 3 (Leaf) | Generates AI feedback using Google Gemini API |

## Installation

### Prerequisites
- Python 3.9+
- Google Gemini API key (get it from https://makersuite.google.com/app/apikey)

### Setup

1. **Install dependencies**:
```bash
cd orchestrator/processing_coordinator/feedback_manager
pip install -r requirements.txt
```

2. **Set up child services**:
```bash
# Install style_selector dependencies
cd style_selector
pip install -r requirements.txt
cd ..

# Install gemini_generator dependencies
cd gemini_generator
pip install -r requirements.txt
cd ..
```

3. **Configure environment variables**:
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_api_key_here
```

4. **Create necessary directories**:
```bash
mkdir -p data/input data/output logs
```

## Configuration

The service is configured via `config.yaml`:

```yaml
manager:
  name: feedback_manager
  version: "1.0.0"

children:
  gemini_generator: "./gemini_generator"
  style_selector: "./style_selector"

input:
  file_path: "../grade_manager/data/output/file_2_3.xlsx"

output:
  file_path: "./data/output/file_3_4.xlsx"

rate_limiting:
  delay_between_calls_seconds: 60

logging:
  level: INFO
  file: "./logs/feedback_manager.log"
```

### Customization Options

- **Rate Limiting**: Adjust `delay_between_calls_seconds` to control API request frequency
- **Logging**: Change log level (DEBUG, INFO, WARNING, ERROR) and file path
- **File Paths**: Customize input/output file locations

## Usage

### As Part of the Orchestrator

The Feedback Manager is typically called by the Processing Coordinator:

```python
from feedback_manager import FeedbackManager

# Initialize manager
manager = FeedbackManager(config_path="config.yaml")

# Process grades and generate feedback
result = manager.process({
    "grade_records": grade_records  # List of GradeRecord objects
})

# Access results
print(f"Generated: {result['generated_count']}")
print(f"Failed: {result['failed_count']}")
print(f"Output: {result['output_file']}")
```

### Standalone Execution

Run the manager independently:

```bash
cd orchestrator/processing_coordinator/feedback_manager

# Process grades from default input file
python -m feedback_manager

# Or specify custom input file
python -m feedback_manager --input ../grade_manager/data/output/file_2_3.xlsx
```

### Command Line Options

```bash
python -m feedback_manager [OPTIONS]

Options:
  --input PATH      Path to input Excel file with grades
  --config PATH     Path to config.yaml (default: ./config.yaml)
  --verbose         Enable verbose logging
  --health          Run health check on all services
```

## Input Specification

**From Parent (Processing Coordinator):**

```python
{
    "grade_records": List[GradeRecord]  # Only records with status="Ready"
}
```

**Input File Format** (`file_2_3.xlsx`):

| Column | Type | Description |
|--------|------|-------------|
| email_id | str | Student email identifier |
| grade | float | Calculated grade (0-100) |
| status | str | "Ready" or "Missing: grade" |

## Output Specification

**To Parent (Processing Coordinator):**

```python
{
    "feedback": List[FeedbackRecord],
    "output_file": str,           # Path to file_3_4.xlsx
    "generated_count": int,       # Successfully generated feedback count
    "failed_count": int           # Failed generation count
}
```

**Output File Format** (`file_3_4.xlsx`):

| Column | Type | Description |
|--------|------|-------------|
| email_id | str | Matching email_id from input |
| reply | str | Generated feedback text (or None) |
| status | str | "Ready" or "Missing: reply" |

## Feedback Styles

The service uses four distinct feedback styles based on grade ranges:

| Grade Range | Style | Description |
|-------------|-------|-------------|
| **90-100** | Trump | Enthusiastic, superlative-heavy ("tremendous", "fantastic", "the best") |
| **70-89** | Hason | Witty, humorous Israeli comedian style |
| **55-69** | Constructive | Helpful, encouraging, improvement-focused |
| **0-54** | Amsalem | Brash, confrontational, direct firebrand style |

## Workflow

1. **Load Grade Records**
   - Read `file_2_3.xlsx` from Grade Manager output
   - Filter for records with status="Ready"

2. **Process Each Grade**
   - Call `style_selector.process({"grade": grade})` → get style & prompt
   - Call `gemini_generator.process({"prompt": prompt, "style": style, "context": {...}})` → get feedback
   - Create FeedbackRecord with email_id and reply

3. **Handle Failures**
   - If Gemini API fails: set reply=None, status="Missing: reply"
   - Log error details for troubleshooting
   - Continue processing remaining records

4. **Write Output**
   - Write all feedback records to `file_3_4.xlsx`
   - Return summary statistics to parent

## Error Handling

The service implements comprehensive error handling:

| Error Type | Handling Strategy |
|------------|-------------------|
| **Missing input file** | Log error, return empty result |
| **Invalid grade data** | Skip record, log warning |
| **Style selection failure** | Use default "constructive" style |
| **Gemini API failure** | Set reply=None, status="Missing: reply" |
| **Rate limit exceeded** | Wait and retry (up to 3 times) |
| **Network timeout** | Log error, mark as failed |

### Failed Records

- Records with failed feedback generation get `reply=None` and `status="Missing: reply"`
- These records can be reprocessed on the next run
- No fallback text is used (only genuine AI feedback proceeds)

## Testing

### Run All Tests

```bash
cd orchestrator/processing_coordinator/feedback_manager

# Run feedback_manager tests
python -m pytest tests/ -v

# Run tests for child services
cd style_selector && python -m pytest tests/ -v && cd ..
cd gemini_generator && python -m pytest tests/ -v && cd ..
```

### Test Coverage

```bash
python -m pytest tests/ -v --cov=feedback_manager --cov-report=html
```

### Health Check

Verify all services are properly configured:

```bash
python -m feedback_manager --health
```

## Logging

Logs are written to both file and console:

- **File**: `./logs/feedback_manager.log`
- **Console**: stdout with colored output
- **Level**: Configurable (DEBUG, INFO, WARNING, ERROR)

### Log Format

```
2026-01-11 10:30:45 | INFO | feedback_manager | Processing 150 grade records
2026-01-11 10:30:46 | INFO | style_selector | Selected style: hason for grade 85.0
2026-01-11 10:31:46 | INFO | gemini_generator | Generated feedback: 78 tokens
2026-01-11 10:31:46 | INFO | feedback_manager | Progress: 1/150 complete
```

## Dependencies

### Python Packages

- `openpyxl>=3.1.0` - Excel file reading/writing
- `pyyaml>=6.0.0` - Configuration file parsing
- `python-dotenv>=1.0.0` - Environment variable management

### Child Services

- `style_selector` - Internal style selection logic
- `gemini_generator` - Gemini API integration

### Shared Modules

- `shared.models.grade_data` - Grade record data models
- `shared.models.feedback_data` - Feedback record data models
- `shared.utils.file_utils` - File I/O utilities
- `shared.interfaces.coordinator_interface` - Parent coordinator interface

## Environment Variables

Required environment variables (set in `.env` file):

```bash
# Google Gemini API key (required)
GEMINI_API_KEY=your_api_key_here

# Optional: Override rate limiting
RATE_LIMIT_DELAY=60

# Optional: Override log level
LOG_LEVEL=INFO
```

## Service Hierarchy

**Parent**: Processing Coordinator (`../`)
**Children**:
- Style Selector (`./style_selector/`)
- Gemini Generator (`./gemini_generator/`)
**Level**: 2 (Task Manager)

## Project Structure

```
feedback_manager/
├── README.md                    # This file
├── PRD.md                       # Product Requirements Document
├── config.yaml                  # Service configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore patterns
├── service.py                   # Main service implementation
├── __init__.py                  # Package initialization
├── __main__.py                  # Standalone execution entry point
├── data/
│   ├── input/                   # Input files (from grade_manager)
│   └── output/                  # Output files (file_3_4.xlsx)
├── logs/                        # Log files
│   └── feedback_manager.log
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_manager.py
├── style_selector/              # Child service (Level 3)
│   ├── README.md
│   ├── PRD.md
│   ├── service.py
│   └── ...
└── gemini_generator/            # Child service (Level 3)
    ├── README.md
    ├── PRD.md
    ├── service.py
    └── ...
```

## Troubleshooting

### Common Issues

**Issue**: "Invalid API key" error
**Solution**: Check that `GEMINI_API_KEY` is set correctly in `.env` file

**Issue**: "Rate limit exceeded"
**Solution**: Increase `delay_between_calls_seconds` in `config.yaml`

**Issue**: "Input file not found"
**Solution**: Verify grade_manager has run successfully and produced `file_2_3.xlsx`

**Issue**: Empty feedback generated
**Solution**: Check Gemini API quota and network connectivity

### Debug Mode

Enable detailed logging:

```bash
python -m feedback_manager --verbose
```

Or set in `config.yaml`:

```yaml
logging:
  level: DEBUG
```

## Performance

- **Processing Time**: ~60 seconds per record (due to rate limiting)
- **API Cost**: ~$0.0001 per feedback (Gemini pricing)
- **Throughput**: ~60 records/hour (with 60s rate limit)

### Optimization Tips

- Reduce `delay_between_calls_seconds` if API quota allows
- Run during off-peak hours to avoid network issues
- Use batch processing for large datasets

## Contributing

When contributing to this service:

1. Maintain the modular architecture (keep logic in child services)
2. Follow the established error handling patterns
3. Update tests for any new functionality
4. Document configuration changes in this README
5. Respect the service hierarchy (Level 2 Task Manager)

## Version

1.0.0

## License

Internal use only - part of the orchestrator system.

## Support

For issues or questions:
- Check logs in `./logs/feedback_manager.log`
- Review child service READMEs for specific issues
- Run health check: `python -m feedback_manager --health`

# Feedback Manager

**Level 2 - Task Manager Service**

A lightweight orchestration service that coordinates feedback generation by managing two child services: **style_selector** (grade-based style selection) and **gemini_generator** (AI feedback generation via Gemini API).

## Purpose

The Feedback Manager is a **thin coordination layer** that:
- Receives parsed grade records from the parent coordinator
- Delegates to child services for actual work
- Manages rate limiting for API calls
- Returns aggregated results to parent

**Note:** Excel I/O is handled by the parent Processing Coordinator.

## Architecture

```
feedback_manager/                    (Level 2 - Orchestrator)
├── style_selector/                  (Level 3 - Style Selection Logic)
└── gemini_generator/                (Level 3 - Gemini API Integration)
```

### Responsibilities by Level

| Level | Service | Responsibility |
|-------|---------|----------------|
| **Level 1** | Processing Coordinator | Excel I/O, file management |
| **Level 2** | Feedback Manager | Orchestration, rate limiting |
| **Level 3** | Style Selector | Style selection logic |
| **Level 3** | Gemini Generator | API calls to Gemini |

## Features

- **Lightweight Orchestration**: Coordinates children without heavy lifting
- **Rate Limiting**: Manages API call frequency
- **Error Handling**: Graceful failure with detailed error messages
- **Health Checks**: Verify child services are properly configured
- **Logging**: Structured logs for debugging

## Installation

### Prerequisites
- Python 3.9+
- Google Gemini API key (for gemini_generator child)

### Setup

```bash
cd orchestrator/processing_coordinator/feedback_manager

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up child services
cd style_selector && pip install -r requirements.txt && cd ..
cd gemini_generator && pip install -r requirements.txt && cd ..

# Configure environment
cp .env.example .env
# Edit .env and add GEMINI_API_KEY
```

Or use the automated setup script:
```bash
./setup.sh
```

## Configuration

The service is configured via `config.yaml`:

```yaml
manager:
  name: feedback_manager
  version: "1.0.0"

children:
  style_selector: "./style_selector"
  gemini_generator: "./gemini_generator"

rate_limiting:
  delay_between_calls_seconds: 60  # Delay between API calls

logging:
  level: INFO
  file: "./logs/feedback_manager.log"
  console: true
```

## Usage

### As Part of the Orchestrator (Primary Use)

```python
from feedback_manager import FeedbackManager

# Initialize manager
manager = FeedbackManager(config_path="config.yaml")

# Parent coordinator provides parsed grade records
grade_records = [
    {'email_id': 'student1@example.com', 'grade': 85.0, 'status': 'Ready'},
    {'email_id': 'student2@example.com', 'grade': 92.0, 'status': 'Ready'},
]

# Process and get feedback
result = manager.process(grade_records)

# Result structure:
# {
#     'feedback': [
#         {'email_id': '...', 'reply': '...', 'status': 'Ready', 'error': None},
#         {'email_id': '...', 'reply': None, 'status': 'Missing: reply', 'error': 'API timeout'},
#     ],
#     'generated_count': 1,
#     'failed_count': 1
# }
```

### Standalone Execution

For health checks and testing:

```bash
# Health check
python -m feedback_manager --health

# With verbose logging
python -m feedback_manager --verbose --health
```

## Input Specification

**From Parent (Processing Coordinator):**

```python
[
    {
        "email_id": str,      # Student identifier
        "grade": float,       # Grade (0-100)
        "status": str         # Should be "Ready"
    },
    ...
]
```

## Output Specification

**To Parent (Processing Coordinator):**

```python
{
    "feedback": [
        {
            "email_id": str,      # Matching email_id
            "reply": str | None,  # Generated feedback (None if failed)
            "status": str,        # "Ready" or "Missing: reply"
            "error": str | None   # Error message if failed
        },
        ...
    ],
    "generated_count": int,       # Successful generations
    "failed_count": int           # Failed generations
}
```

## Workflow

1. **Receive grade records** from parent coordinator (already parsed from Excel)
2. **For each record:**
   - Call `style_selector.process({'grade': grade})` → get style & prompt
   - Call `gemini_generator.process({'prompt': prompt, 'style': style, 'context': {...}})` → get feedback
   - Build feedback record with email_id, reply, status, error
3. **Apply rate limiting** between API calls
4. **Return aggregated results** to parent

## Feedback Styles

The style_selector child determines style based on grade:

| Grade Range | Style | Description |
|-------------|-------|-------------|
| **90-100** | Trump | Enthusiastic, superlative-heavy |
| **70-89** | Hason | Witty, humorous Israeli comedian style |
| **55-69** | Constructive | Helpful, encouraging |
| **0-54** | Amsalem | Brash, confrontational |

## Error Handling

| Error Type | Handling |
|------------|----------|
| **Style selection fails** | Log error, mark as failed with error message |
| **Gemini API fails** | Set reply=None, status="Missing: reply", include error |
| **Network timeout** | Return failed status with timeout error |
| **Invalid grade data** | Log error, skip record with error message |

All errors are:
- Logged with details
- Returned in the error field of the feedback record
- Counted in `failed_count`

## Testing

### Run Tests

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

### Run with Coverage

```bash
python -m pytest tests/ -v --cov=service
```

### Health Check

```bash
python -m feedback_manager --health
```

Expected output:
```
feedback_manager................ OK
style_selector.................. OK
gemini_generator................ OK (API not tested)
```

## Child Services

### Style Selector (`./style_selector/`)
- **Purpose**: Select feedback style based on grade
- **Type**: Internal logic (no external API)
- **Input**: `{'grade': float}`
- **Output**: `{'style_name': str, 'style_description': str, 'prompt_template': str}`

See `style_selector/README.md` for details.

### Gemini Generator (`./gemini_generator/`)
- **Purpose**: Generate AI feedback using Google Gemini API
- **Type**: External API integration
- **Input**: `{'prompt': str, 'style': str, 'context': dict}`
- **Output**: `{'feedback': str|None, 'status': str, 'error': str|None, 'tokens_used': int}`

See `gemini_generator/README.md` for details.

## Logging

Logs are written to both file and console:

- **File**: `./logs/feedback_manager.log`
- **Console**: stdout (configurable)
- **Level**: INFO (configurable: DEBUG, INFO, WARNING, ERROR)

### Log Format
```
2026-01-15 10:30:45 | INFO | feedback_manager | Starting feedback generation for 10 records
2026-01-15 10:30:46 | DEBUG | feedback_manager | Selected style 'hason' for grade 85.0
2026-01-15 10:31:46 | INFO | feedback_manager | Successfully generated feedback for student@example.com
```

## Dependencies

### Python Packages
- `pyyaml>=6.0.0` - Configuration parsing
- `python-dotenv>=1.0.0` - Environment variable management

### Child Services
- `style_selector` - Style selection logic
- `gemini_generator` - Gemini API integration (requires API key)

## Project Structure

```
feedback_manager/
├── README.md                    # This file
├── PRD.md                       # Product Requirements Document
├── config.yaml                  # Service configuration (no file paths)
├── requirements.txt             # Minimal dependencies
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore patterns
├── service.py                   # Orchestration logic (~310 lines)
├── __init__.py                  # Package initialization
├── __main__.py                  # Standalone entry point
├── setup.sh                     # Setup script
├── logs/                        # Log files
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_manager.py
├── style_selector/              # Child service (Level 3)
│   └── ...
└── gemini_generator/            # Child service (Level 3)
    └── ...
```

## Design Philosophy

This service follows the **separation of concerns** principle:

- **Parent Coordinator**: Handles file I/O, data persistence
- **Feedback Manager**: Orchestrates workflow, manages rate limiting
- **Child Services**: Perform specific tasks (style selection, API calls)

By keeping responsibilities separate:
- Each service is easier to test
- Logic is easier to understand
- Changes are localized
- Services can be reused independently

## Performance

- **Processing Time**: ~60 seconds per record (rate limit dependent)
- **API Cost**: Depends on Gemini usage (see gemini_generator docs)
- **Throughput**: Configurable via `delay_between_calls_seconds`

## Troubleshooting

### Common Issues

**Issue**: Child service initialization fails
**Solution**: Ensure child services are properly installed with dependencies

**Issue**: "No module named 'google.generativeai'"
**Solution**: Install gemini_generator dependencies: `cd gemini_generator && pip install -r requirements.txt`

**Issue**: Health check shows gemini_generator failed
**Solution**: Check GEMINI_API_KEY in .env file

### Debug Mode

```bash
python -m feedback_manager --verbose --health
```

## Version

1.0.0

## License

Internal use only - part of the orchestrator system.

# Processing Coordinator

Level 1 domain coordinator for repository processing operations.

## Overview

Coordinates processing operations by delegating to Level 2 managers:
- **Grade Manager**: Clones repos and calculates grades
- **Feedback Manager**: Generates AI-powered feedback

## Installation

```bash
cd orchestrator/processing_coordinator
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to configure:
- Child manager paths
- Logging settings

## Usage

### Standalone Execution
```bash
# Health check
python -m processing_coordinator --action health

# Grade repositories
python -m processing_coordinator --action grade --input ../email_coordinator/email_reader/data/output/file_1_2.xlsx
```

### As Library
```python
from processing_coordinator.coordinator import ProcessingCoordinator

coordinator = ProcessingCoordinator(config_path="config.yaml")

# Grade repositories
result = coordinator.grade(email_records)

# Generate feedback
result = coordinator.generate_feedback(grade_records)
```

## Actions

| Action | Description | Input | Output |
|--------|-------------|-------|--------|
| `grade` | Clone & grade repos | file_1_2.xlsx | file_2_3.xlsx |
| `feedback` | Generate AI feedback | file_2_3.xlsx | file_3_4.xlsx |
| `full_pipeline` | Both operations | file_1_2.xlsx | Both files |

## Project Structure

```
processing_coordinator/
├── coordinator.py       # Main coordinator
├── config.yaml         # Configuration
├── requirements.txt    # Dependencies
├── PRD.md             # Product requirements
├── README.md          # This file
├── grade_manager/     # Level 2 - Grading
└── feedback_manager/  # Level 2 - Feedback
```

## Testing

```bash
python -m pytest tests/ -v
```

## Logging

Logs: `./logs/processing_coordinator.log`

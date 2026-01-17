# Homework Grading System - Orchestrator

Level 0 root coordinator for the BTS (Binomial Tree Structure) homework grading system.

## Overview

The Orchestrator is the main entry point that coordinates the complete homework grading workflow by delegating to Level 1 coordinators:

- **Email Coordinator**: Handles email reading and draft creation
- **Processing Coordinator**: Handles grading and feedback generation

## Installation

```bash
cd orchestrator
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to configure:
- Processing modes (test, batch, full)
- Child coordinator paths
- Logging settings

## Usage

### Interactive Mode
```bash
python main.py
```

### Command Line Mode
```bash
# Run specific step
python main.py --mode test --step 1

# Run all steps
python main.py --mode batch --batch-size 10 --step all

# Health check
python main.py --health
```

## Workflow Steps

| Step | Description | Coordinator |
|------|-------------|-------------|
| 1 | Search & Parse Emails | email_coordinator |
| 2 | Clone & Grade Repos | processing_coordinator |
| 3 | Generate AI Feedback | processing_coordinator |
| 4 | Create Email Drafts | email_coordinator |

## Project Structure

```
orchestrator/
├── main.py              # Main entry point with CLI
├── config.yaml          # Configuration
├── requirements.txt     # Dependencies
├── PRD.md              # Product requirements
├── README.md           # This file
├── email_coordinator/   # Level 1 - Email operations
└── processing_coordinator/  # Level 1 - Processing operations
```

## Testing

```bash
python -m pytest tests/ -v
```

## Logging

Logs are written to `./logs/orchestrator.log`. Configure log level in `config.yaml`.

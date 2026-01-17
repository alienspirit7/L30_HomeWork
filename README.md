# Homework Grading System

An automated system for processing student homework submissions via Gmail, cloning GitHub repositories, analyzing code, generating AI-powered feedback, and creating personalized email draft responses.

Built with **Binomial Tree Structure (BTS)** architecture where each component is a standalone service.

> **📌 Original Project:** This is a re-implementation using BTS architecture. See the initial project: [L19_HomeWork](https://github.com/alienspirit7/L19_HomeWork.git)

## Architecture

```
Level 0: orchestrator/                    ROOT COORDINATOR
         ├── main.py                      Interactive CLI entry point
         │
Level 1: ├── email_coordinator/           EMAIL OPERATIONS
         │   ├── coordinator.py           Coordinates email + drafts
         │   │
Level 2: │   ├── email_reader/            INBOUND EMAILS
         │   │   ├── manager.py           Orchestrates gmail + parsing
Level 3: │   │   ├── gmail_reader/        Fetches from Gmail API
         │   │   └── email_parser/        Parses email content
         │   │
Level 2: │   └── draft_manager/           OUTBOUND DRAFTS
         │       ├── manager.py           Orchestrates drafts
Level 3: │       ├── draft_composer/      Creates Gmail drafts
         │       └── student_mapper/      Maps emails to names
         │
Level 1: └── processing_coordinator/      PROCESSING OPERATIONS
             ├── coordinator.py           Coordinates grading + feedback
             │
Level 2:     ├── grade_manager/           GRADING
             │   ├── service.py           Orchestrates cloning + analysis
Level 3:     │   ├── github_cloner/       Clones repositories
             │   └── python_analyzer/     Analyzes Python code
             │
Level 2:     └── feedback_manager/        AI FEEDBACK
                 ├── service.py           Orchestrates feedback generation
Level 3:         ├── gemini_generator/    Calls Gemini API
                 └── style_selector/      Selects feedback style

Utility:  shared/                         SHARED COMPONENTS
          ├── models/                     Data models
          ├── utils/                      Utilities
          ├── interfaces/                 Abstract base classes
          └── config/                     Configuration management
```

## Quick Start

```bash
# Clone repository
git clone <repository-url>
cd L30_HomeWork

# Install dependencies
cd orchestrator
pip install -r requirements.txt

# Configure APIs (see Configuration section)

# Run orchestrator
python main.py
```

## Workflow

| Step | Description | Module | Output |
|------|-------------|--------|--------|
| 1 | Search & Parse Emails | email_reader | file_1_2.xlsx |
| 2 | Clone & Grade Repos | grade_manager | file_2_3.xlsx |
| 3 | Generate AI Feedback | feedback_manager | file_3_4.xlsx |
| 4 | Create Email Drafts | draft_manager | Gmail drafts |

## Standalone Services

Each module can run independently:

```bash
# Email Reader
cd orchestrator/email_coordinator/email_reader
python -m manager --mode test

# Grade Manager
cd orchestrator/processing_coordinator/grade_manager
python -m grade_manager --input <file_1_2.xlsx>

# Feedback Manager
cd orchestrator/processing_coordinator/feedback_manager
python -m feedback_manager --input <file_2_3.xlsx>

# Draft Manager
cd orchestrator/email_coordinator/draft_manager
python -m draft_manager --help
```

## Configuration

Each module has its own `config.yaml`. Key configurations:

### Gmail API
1. Create project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download `credentials.json` to `config/`

### Gemini API
1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create `.env` file: `GEMINI_API_KEY=your-key`

## Testing

Run tests for any module:

```bash
# All orchestrator tests
cd orchestrator && python -m pytest tests/ -v

# Specific module tests
cd orchestrator/email_coordinator && python -m pytest tests/ -v
cd orchestrator/processing_coordinator && python -m pytest tests/ -v
cd shared && python -m pytest tests/ -v
```

## Project Structure

Each standalone module includes:
- `README.md` - Documentation
- `PRD.md` - Product requirements
- `config.yaml` - Configuration
- `requirements.txt` - Dependencies
- `tests/` - Test suite
- `logs/` - Log files

## Logging

Logs are written to `./logs/` in each module. Configure log level in `config.yaml`:

```yaml
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  file: "./logs/module.log"
```

## License

MIT License - See LICENSE file for details.

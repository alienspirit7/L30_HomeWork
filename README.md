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

## Module Descriptions

### Level 0: Orchestrator (Root)

| Module | Description |
|--------|-------------|
| **orchestrator** | Main entry point with interactive CLI. Coordinates the complete homework grading workflow by delegating to Level 1 coordinators. Supports test (1 email), batch (N emails), and full (all unread) modes. |

### Level 1: Domain Coordinators

| Module | Description |
|--------|-------------|
| **email_coordinator** | Coordinates all email-related operations. Manages inbound email reading via `email_reader` and outbound draft creation via `draft_manager`. |
| **processing_coordinator** | Coordinates processing operations. Manages repository grading via `grade_manager` and AI feedback generation via `feedback_manager`. |

### Level 2: Task Managers

| Module | Description |
|--------|-------------|
| **email_reader** | Fetches unread emails from Gmail API and parses them to extract homework submission data (repo URLs, sender info, timestamps). Outputs `file_1_2.xlsx`. |
| **draft_manager** | Creates personalized Gmail draft responses. Maps student emails to names and composes professional feedback emails with grades. |
| **grade_manager** | Clones GitHub repositories and calculates grades based on Python code analysis. Supports parallel cloning with configurable workers. Outputs `file_2_3.xlsx`. |
| **feedback_manager** | Generates AI-powered feedback using Google Gemini API. Selects appropriate feedback style based on grade (trump/hason/constructive/amsalem). Outputs `file_3_4.xlsx`. |

### Level 3: Leaf Services

| Module | Description |
|--------|-------------|
| **gmail_reader** | Authenticates with Gmail API using OAuth2 and fetches unread emails matching homework subject pattern. Returns raw email data. |
| **email_parser** | Parses raw email content to extract: sender email, subject, timestamp, and GitHub repository URL from email body. Validates extracted data. |
| **github_cloner** | Clones GitHub repositories to local filesystem with timeout protection. Supports shallow cloning (`--depth 1`) for efficiency. Handles authentication errors gracefully. |
| **python_analyzer** | Analyzes Python files in cloned repositories. Counts lines of code (excluding comments, docstrings, blank lines). Calculates grade based on formula: `(lines_above_150 / total_lines) * 100`. |
| **style_selector** | Determines feedback style based on grade: **trump** (90+), **hason** (70-89), **constructive** (55-69), **amsalem** (<55). Each style has distinct tone and messaging. |
| **gemini_generator** | Calls Google Gemini API to generate personalized feedback text. Uses grade and style to craft appropriate response with retry logic for API failures. |
| **student_mapper** | Maps email addresses to student names using Excel lookup table (`students.xlsx`). Enables personalized greeting in draft emails. |
| **draft_composer** | Creates Gmail draft emails via API. Formats feedback with grade, personalized message, and instructor signature. Sets reply-to original thread. |

### Utility: Shared Module

| Component | Description |
|-----------|-------------|
| **models/** | Data classes: `EmailRecord`, `GradeRecord`, `FeedbackRecord`, `StudentRecord` with status tracking and serialization. |
| **utils/** | Utilities: `sha256_hash` (email hashing), `validate_email`/`validate_github_url` (validation), `read_excel`/`write_excel` (file I/O), `get_logger` (logging). |
| **interfaces/** | Abstract base classes: `ServiceInterface` (Level 3 leaves), `CoordinatorInterface` (Level 1-2 nodes). |
| **config/** | Configuration: `BaseConfig` (YAML loading), `load_env` (.env file loading). |


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
# Create virtual environment (first time)
python3 -m venv venv && source venv/bin/activate
pip install pytest pyyaml python-dotenv openpyxl

# All orchestrator tests
cd orchestrator && python -m pytest tests/ -v

# Specific module tests
cd orchestrator/email_coordinator && python -m pytest tests/ -v
cd orchestrator/processing_coordinator && python -m pytest tests/ -v
cd shared && python -m pytest tests/ -v
```

### Test Results (Shared Module)

```
==== test session starts ====
platform darwin -- Python 3.9.6, pytest-8.4.2
collected 31 items

tests/test_models.py::TestEmailData::test_email_status_values PASSED
tests/test_models.py::TestEmailData::test_email_record_creation PASSED
tests/test_models.py::TestEmailData::test_email_record_not_ready PASSED
tests/test_models.py::TestEmailData::test_email_record_to_dict PASSED
tests/test_models.py::TestEmailData::test_email_record_from_dict PASSED
tests/test_models.py::TestGradeData::test_analysis_result_grade_calculation PASSED
tests/test_models.py::TestGradeData::test_analysis_result_zero_lines PASSED
tests/test_models.py::TestGradeData::test_grade_record_creation PASSED
tests/test_models.py::TestGradeData::test_grade_record_to_dict PASSED
tests/test_models.py::TestFeedbackData::test_style_type_from_grade_trump PASSED
tests/test_models.py::TestFeedbackData::test_style_type_from_grade_hason PASSED
tests/test_models.py::TestFeedbackData::test_style_type_from_grade_constructive PASSED
tests/test_models.py::TestFeedbackData::test_style_type_from_grade_amsalem PASSED
tests/test_models.py::TestFeedbackData::test_feedback_record_is_ready PASSED
tests/test_models.py::TestFeedbackData::test_feedback_record_not_ready PASSED
tests/test_models.py::TestStudentData::test_student_record_creation PASSED
tests/test_models.py::TestStudentData::test_student_record_to_dict PASSED
tests/test_utils.py::TestHashUtils::test_sha256_hash_returns_string PASSED
tests/test_utils.py::TestHashUtils::test_sha256_hash_consistent PASSED
tests/test_utils.py::TestHashUtils::test_sha256_hash_different_inputs PASSED
tests/test_utils.py::TestHashUtils::test_sha256_hash_length PASSED
tests/test_utils.py::TestHashUtils::test_generate_id_single_component PASSED
tests/test_utils.py::TestHashUtils::test_generate_id_multiple_components PASSED
tests/test_utils.py::TestHashUtils::test_generate_id_consistent PASSED
tests/test_utils.py::TestHashUtils::test_generate_id_order_matters PASSED
tests/test_utils.py::TestValidators::test_validate_email_valid PASSED
tests/test_utils.py::TestValidators::test_validate_email_invalid PASSED
tests/test_utils.py::TestValidators::test_validate_github_url_valid PASSED
tests/test_utils.py::TestValidators::test_validate_github_url_invalid PASSED
tests/test_utils.py::TestValidators::test_extract_repo_name_valid PASSED
tests/test_utils.py::TestValidators::test_extract_repo_name_invalid PASSED

==== 31 passed in 0.07s ====
```

| Module | Tests | Status |
|--------|-------|--------|
| EmailData | 5 | ✅ Passed |
| GradeData | 4 | ✅ Passed |
| FeedbackData | 6 | ✅ Passed |
| StudentData | 2 | ✅ Passed |
| HashUtils | 8 | ✅ Passed |
| Validators | 6 | ✅ Passed |
| **Total** | **31** | ✅ **All Passed** |

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

# Draft Manager - Quick Start Guide

Get the Draft Manager up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- Google Cloud account (for Gmail API)
- Student email-to-name mapping data

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd draft_manager

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Child Services

#### Student Mapper

```bash
cd student_mapper

# Install dependencies
pip install -r requirements.txt

# Create sample data (or provide your own Excel file)
python create_sample_data.py

# Verify setup
python -m src --email "student1@example.com"
```

Expected output:
```
==================================================
Email: student1@example.com
Name: Alex Johnson
Found: Yes
==================================================
```

#### Draft Composer

```bash
cd ../draft_composer

# Install dependencies
pip install -r requirements.txt

# Set up Gmail API credentials
# 1. Go to https://console.cloud.google.com/
# 2. Create a project
# 3. Enable Gmail API
# 4. Create OAuth 2.0 credentials (Desktop app)
# 5. Download and save as data/credentials/credentials.json

mkdir -p data/credentials
# Place your credentials.json in data/credentials/

# First run will open browser for authentication
```

### 3. Run Draft Manager

```bash
cd ..  # Back to draft_manager root

# Test with sample data
python -m draft_manager \
    --email-file tests/fixtures/sample_emails.xlsx \
    --feedback-file tests/fixtures/sample_feedback.xlsx \
    --dry-run
```

## Programmatic Usage

```python
from draft_manager import DraftManager

# Initialize
manager = DraftManager()

# Prepare input data
input_data = {
    "email_records": [
        {
            "email_id": "msg_123",
            "sender_email": "student1@example.com",
            "thread_id": "thread_abc",
            "repo_url": "https://github.com/student/repo",
            "subject": "Homework Question"
        }
    ],
    "feedback_records": [
        {
            "email_id": "msg_123",
            "feedback": "Great work! Your code is clean and well-tested.",
            "status": "Ready"
        }
    ]
}

# Process drafts
result = manager.process(input_data)

print(f"Created: {result['drafts_created']}")
print(f"Failed: {result['drafts_failed']}")
```

## Common Tasks

### Update Student Mappings

```bash
# Edit the Excel file
open student_mapper/data/students_mapping.xlsx

# Or generate new sample data
cd student_mapper
python create_sample_data.py
```

### Customize Email Template

Edit `config.yaml`:

```yaml
email_template:
  greeting: "Hello {name},"  # Change greeting
  signature: "Best regards, Dr. Smith"  # Change signature
  repo_line: "Repository: {repo_url}"  # Change repo line
```

### Run Tests

```bash
# Test everything
pytest tests/ -v

# Test with coverage
pytest tests/ -v --cov=. --cov-report=html
```

### View Logs

```bash
# Manager logs
tail -f logs/draft_manager.log

# Child service logs
tail -f student_mapper/logs/student_mapper.log
tail -f draft_composer/logs/draft_composer.log
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Ensure you're in the correct directory and dependencies are installed:
```bash
cd draft_manager
pip install -r requirements.txt
cd student_mapper && pip install -r requirements.txt && cd ..
cd draft_composer && pip install -r requirements.txt && cd ..
```

### Issue: Gmail Authentication Failed

**Solution**: Delete the token and re-authenticate:
```bash
rm draft_composer/data/credentials/token.json
# Run draft_composer again - browser will open for auth
```

### Issue: Student Names Not Found

**Solution**: Check Excel file structure:
```bash
cd student_mapper
python -c "import pandas as pd; print(pd.read_excel('data/students_mapping.xlsx').head())"
```

Ensure columns match config:
- `email_address` column exists
- `name` column exists

## Next Steps

- Read the full [README.md](README.md) for comprehensive documentation
- Review [PRD.md](PRD.md) for detailed specifications
- Check child service documentation:
  - [Draft Composer README](draft_composer/README.md)
  - [Student Mapper README](student_mapper/README.md)

## Support

For issues or questions:
1. Check the logs in `./logs/`
2. Review [README.md](README.md) troubleshooting section
3. Run tests to verify setup: `pytest tests/ -v`

Happy drafting!

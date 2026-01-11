# Gemini Generator Service

**Level 3 - Leaf Service**

Generates AI-powered feedback using Google's Gemini API with rate limiting and retry logic.

## Features

- Google Gemini API integration
- Rate limiting (configurable delay between requests)
- Automatic retry logic with exponential backoff
- Comprehensive error handling
- Structured logging
- Standalone execution support
- Full test coverage

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. Get your Gemini API key from: https://makersuite.google.com/app/apikey

## Configuration

Edit `config.yaml` to customize:
- API model selection
- Rate limiting parameters
- Generation settings (max tokens, temperature)
- Logging configuration

## Usage

### As a Module

```python
from gemini_generator import GeminiGeneratorService

# Initialize service
service = GeminiGeneratorService()

# Prepare input
input_data = {
    "prompt": "Generate feedback for student assignment",
    "style": "constructive",
    "context": {
        "grade": 85.0,
        "email_id": "student@example.com"
    }
}

# Generate feedback
result = service.process(input_data)

print(f"Status: {result['status']}")
print(f"Feedback: {result['feedback']}")
print(f"Tokens Used: {result['tokens_used']}")
```

### Standalone Execution

```bash
python -m gemini_generator \
  --prompt "Generate feedback for student" \
  --style "constructive" \
  --grade 85.0 \
  --email-id "student@example.com"
```

### Health Check

```bash
python -m gemini_generator --health
```

## Input Specification

```python
{
    "prompt": str,              # Full prompt text
    "style": str,               # Feedback style
    "context": {
        "grade": float,         # Student grade
        "email_id": str         # Email identifier
    }
}
```

## Output Specification

```python
{
    "feedback": str | None,     # Generated feedback (None on failure)
    "status": str,              # "Success" | "Failed"
    "error": str | None,        # Error message if failed
    "tokens_used": int          # Approximate token count
}
```

## Rate Limiting

- **Request delay**: 60 seconds (configurable)
- **Max retries**: 3
- **Retry delay**: 5 seconds

## Error Handling

| Error Type | Handling |
|------------|----------|
| Rate limit | Wait and retry (up to 3 times) |
| API timeout | Return Failed + error |
| Invalid API key | Return Failed + "Invalid API key" |
| Network error | Retry, then return Failed |

On failure, returns `feedback=None` so parent service can set status="Missing: reply"

## Testing

Run the test suite:
```bash
cd orchestrator/processing_coordinator/feedback_manager/gemini_generator
python -m pytest tests/ -v
```

## Logging

Logs are written to `./logs/gemini_generator.log` and also displayed on console.

Log level can be configured in `config.yaml` (default: INFO).

## Dependencies

- `google-generativeai>=0.3.0` - Google Gemini API client
- `python-dotenv>=1.0.0` - Environment variable management
- `pyyaml>=6.0.0` - YAML configuration parsing
- `pytest>=7.0.0` - Testing framework

## Service Hierarchy

**Parent**: Feedback Manager (`../`)
**Children**: None (Leaf node)
**Level**: 3 (Leaf Service)

## Environment Variables

Required:
- `GEMINI_API_KEY` - Your Google Gemini API key

## Notes

- This is a **leaf service** with **external API access**
- Implements proper rate limiting to respect API quotas
- Returns `None` for feedback on failure (parent will handle missing reply status)
- Token usage is approximated based on input/output word counts

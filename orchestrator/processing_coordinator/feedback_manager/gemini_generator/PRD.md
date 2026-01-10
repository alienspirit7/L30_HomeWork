# Gemini Generator Service PRD (Level 3 - Leaf 7)

## Purpose
Generates AI-powered feedback using Google's Gemini API. Implements rate limiting and retry logic. This is a **leaf service** with **external API access**.

## Level
3 (Leaf Service)

## Parent
| Parent | Path |
|--------|------|
| Feedback Manager | `../` |

## Children
None (Leaf node)

## External API
**Google Gemini API**

---

## Input Specification

**From Parent (Feedback Manager):**
```python
{
    "prompt": str,              # Full prompt text
    "style": str,               # Style name from Style Selector
    "context": {
        "grade": float,
        "student_name": str
    }
}
```

## Output Specification

**To Parent (Feedback Manager):**
```python
{
    "feedback": str | None,
    "status": str,              # "Success" | "Failed"
    "error": str | None,
    "tokens_used": int
}
```

---

## Rate Limiting

| Parameter | Value |
|-----------|-------|
| Request delay | 60 seconds (configurable) |
| Max retries | 3 |
| Retry delay | 5 seconds |

---

## Configuration

`config.yaml`:
```yaml
service:
  name: gemini_generator
  version: "1.0.0"

gemini:
  api_key_env: "GEMINI_API_KEY"
  model: "gemini-pro"
  
rate_limiting:
  request_delay_seconds: 60
  max_retries: 3
  retry_delay_seconds: 5

generation:
  max_tokens: 500
  temperature: 0.7

logging:
  level: INFO
  file: "./logs/gemini_generator.log"
```

`requirements.txt`:
```
google-generativeai>=0.3.0
python-dotenv>=1.0.0
```

---

## Environment Variables

```bash
# Required in .env
GEMINI_API_KEY=your_api_key_here
```

---

## Error Handling

| Error Type | Handling |
|------------|----------|
| Rate limit | Wait and retry (up to 3 times) |
| API timeout | Return Failed + error |
| Invalid API key | Return Failed + "Invalid API key" |
| Network error | Retry, then return Failed |

**Important:** On failure, returns `feedback=None` so parent can set status="Missing: reply"

---

## Dependencies
- `shared.interfaces.service_interface`
- `shared.utils.logger`
- `shared.config.env_loader`

---

## Testing
```bash
cd orchestrator/processing_coordinator/feedback_manager/gemini_generator
python -m pytest tests/ -v
```

## Standalone Run
```bash
cd orchestrator/processing_coordinator/feedback_manager/gemini_generator
python -m service --prompt "Generate feedback for student" --style "constructive"
```

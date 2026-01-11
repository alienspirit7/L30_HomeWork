# GitHub Cloner Service

A lightweight, efficient service for cloning GitHub repositories with timeout protection and comprehensive error handling. Part of the Grade Manager orchestrator system.

## Overview

GitHub Cloner Service is a Level 3 leaf service that provides reliable repository cloning functionality with:
- Shallow cloning for speed optimization
- Configurable timeout protection
- Parallel cloning support
- Automatic cleanup on failures
- Comprehensive error handling and logging

## Features

- **Fast Cloning**: Uses shallow clone (`--depth 1`) for improved performance
- **Timeout Protection**: Prevents hanging operations with configurable timeouts
- **Error Handling**: Gracefully handles invalid URLs, private repos, network errors, and timeouts
- **Logging**: Dual logging to file and console with configurable log levels
- **Cleanup**: Automatic cleanup on failures and manual cleanup methods
- **Flexible Configuration**: YAML-based configuration with sensible defaults
- **Service Interface**: Compatible with parent Grade Manager service

## Installation

### Prerequisites
- Python 3.7+
- Git CLI installed and available in PATH

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Standalone Execution

**Basic usage:**
```bash
python -m service --url "https://github.com/octocat/Hello-World"
```

**With custom destination:**
```bash
python -m service --url "https://github.com/user/repo" --dest "./my_repos/repo"
```

**With custom timeout:**
```bash
python -m service --url "https://github.com/user/repo" --timeout 120
```

**With custom config file:**
```bash
python -m service --url "https://github.com/user/repo" --config "./custom_config.yaml"
```

### Python API

**Basic usage:**
```python
from service import GitHubClonerService

# Initialize service
service = GitHubClonerService()

# Clone repository
result = service.clone_repository("https://github.com/octocat/Hello-World")

# Check result
if result['status'] == 'Success':
    print(f"Repository cloned to: {result['clone_path']}")
    print(f"Duration: {result['duration_seconds']:.2f}s")
else:
    print(f"Clone failed: {result['error']}")
```

**With custom parameters:**
```python
# Clone with custom destination and timeout
result = service.clone_repository(
    repo_url="https://github.com/user/repo",
    destination_dir="./my_repos/custom_location",
    timeout_seconds=120
)
```

**Using the process interface (for parent services):**
```python
# Input format expected by parent service
input_data = {
    'repo_url': 'https://github.com/user/repo',
    'destination_dir': './repos/user_repo',  # Optional
    'timeout_seconds': 60                     # Optional
}

# Process the request
result = service.process(input_data)

# Output format
# {
#     'clone_path': '/absolute/path/to/repo',
#     'status': 'Success' | 'Failed',
#     'error': None | 'Error message',
#     'duration_seconds': 1.23
# }
```

**Cleanup:**
```python
# Clean up cloned repository
success = service.cleanup_repository(result['clone_path'])
```

## Configuration

The service uses `config.yaml` for configuration. If not found, it uses sensible defaults.

### config.yaml

```yaml
service:
  name: github_cloner
  version: "1.0.0"

git:
  command: "git"
  clone_args: ["--depth", "1"]  # Shallow clone for speed

defaults:
  timeout_seconds: 60
  temp_directory: "./data/tmp/repos"
  max_workers: 5

cleanup:
  delete_after_use: true

logging:
  level: INFO
  file: "./logs/github_cloner.log"
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `git.command` | `git` | Git command to use |
| `git.clone_args` | `["--depth", "1"]` | Arguments for git clone |
| `defaults.timeout_seconds` | `60` | Default timeout in seconds |
| `defaults.temp_directory` | `./data/tmp/repos` | Default clone directory |
| `defaults.max_workers` | `5` | Max parallel workers (future use) |
| `cleanup.delete_after_use` | `true` | Auto cleanup after use |
| `logging.level` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `logging.file` | `./logs/github_cloner.log` | Log file path |

## Supported URL Formats

- `https://github.com/username/repo-name`
- `https://github.com/username/repo-name.git`
- `http://github.com/username/repo-name` (auto-upgraded to HTTPS)

## API Reference

### GitHubClonerService

#### `__init__(config_path: str = "config.yaml")`
Initialize the service with optional config file path.

#### `clone_repository(repo_url: str, destination_dir: Optional[str] = None, timeout_seconds: Optional[int] = None) -> Dict`
Clone a GitHub repository.

**Parameters:**
- `repo_url` (str): GitHub repository URL
- `destination_dir` (str, optional): Destination directory path
- `timeout_seconds` (int, optional): Timeout in seconds

**Returns:**
```python
{
    'clone_path': str | None,      # Absolute path to cloned repo
    'status': str,                  # 'Success' | 'Failed'
    'error': str | None,           # Error message if failed
    'duration_seconds': float      # Operation duration
}
```

#### `cleanup_repository(clone_path: str) -> bool`
Clean up a cloned repository.

**Parameters:**
- `clone_path` (str): Path to repository to delete

**Returns:**
- `bool`: True if cleanup successful, False otherwise

#### `process(input_data: Dict) -> Dict`
Process interface for parent services.

**Parameters:**
```python
{
    'repo_url': str,
    'destination_dir': str,  # Optional
    'timeout_seconds': int   # Optional
}
```

**Returns:** Same as `clone_repository()`

## Error Handling

| Error Type | Status | Error Message |
|------------|--------|---------------|
| Invalid URL | Failed | "Invalid URL format: ..." |
| Repository not found | Failed | "Repository not found" |
| Private repo / Auth required | Failed | "Access denied (private repository...)" |
| Network error | Failed | "Network error" |
| Timeout | Failed | "Clone operation timed out after X seconds" |
| Unexpected error | Failed | "Unexpected error: ..." |

## Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Test

```bash
python -m pytest tests/test_service.py::TestGitHubClonerService::test_clone_success -v
```

### Run with Coverage

```bash
python -m pytest tests/ --cov=service --cov-report=html
```

## Project Structure

```
github_cloner/
├── README.md              # This file
├── PRD.md                 # Product requirements document
├── config.yaml            # Service configuration
├── requirements.txt       # Python dependencies
├── service.py             # Main service implementation
├── __init__.py           # Package initialization
├── __main__.py           # Module entry point
├── .gitignore            # Git ignore patterns
├── data/
│   └── tmp/
│       └── repos/        # Repository clone directory
├── logs/                 # Log files directory
└── tests/
    ├── __init__.py
    └── test_service.py   # Comprehensive test suite
```

## Integration

### Parent Service Integration

The GitHub Cloner service is designed to be called by the Grade Manager service:

```python
# In Grade Manager
from github_cloner import GitHubClonerService

cloner = GitHubClonerService()

# Clone student submission
result = cloner.process({
    'repo_url': student_repo_url,
    'destination_dir': f'./data/tmp/repos/{student_email}/',
    'timeout_seconds': 60
})

if result['status'] == 'Success':
    # Proceed with grading
    grade_submission(result['clone_path'])

    # Cleanup
    cloner.cleanup_repository(result['clone_path'])
```

## Dependencies

- **pyyaml**: YAML configuration file parsing
- **pytest**: Testing framework

All other functionality uses Python standard library (subprocess, logging, pathlib, etc.)

## Logging

Logs are written to both file and console:

**Log file location:** `./logs/github_cloner.log` (configurable)

**Log format:**
```
2026-01-11 10:30:45,123 - service - INFO - Cloning https://github.com/user/repo to ./data/tmp/repos/repo with timeout 60s
2026-01-11 10:30:47,456 - service - INFO - Successfully cloned https://github.com/user/repo in 2.33s
```

## Performance

- **Shallow clones** reduce clone time by 70-90% for large repositories
- **Timeout protection** prevents resource exhaustion
- **Parallel cloning support** (up to 5 workers configured)

## Limitations

- Only supports public GitHub repositories (or repos with SSH keys configured in system)
- Requires Git CLI installed on the system
- Shallow clones (`--depth 1`) don't include full history

## Troubleshooting

### "Invalid URL format" error
Ensure URL starts with `https://github.com/` or `http://github.com/`

### "Access denied" error
Repository is private or requires authentication. Configure SSH keys or use access tokens.

### "Clone operation timed out" error
Increase timeout value or check network connection.

### Git command not found
Ensure Git is installed and available in system PATH:
```bash
git --version
```

## License

Part of the Grade Manager orchestrator system.

## Version

Current version: **1.0.0**

---

**Level:** 3 (Leaf Service)
**Parent:** Grade Manager (`../`)
**External Dependencies:** Git CLI

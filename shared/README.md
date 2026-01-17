# Shared Module

Centralized library of reusable components for all BTS (Binomial Tree Structure) modules.

## Overview

The shared module provides common utilities, data models, interfaces, and configuration management used by all modules in the homework grading system.

## Installation

```bash
cd shared
pip install -r requirements.txt
```

## Components

### Models (`models/`)
Data structures used across modules:
- `EmailRecord`, `EmailStatus` - Email data
- `GradeRecord`, `AnalysisResult` - Grading data
- `FeedbackRecord`, `StyleType` - Feedback data
- `StudentRecord` - Student mapping data

### Utils (`utils/`)
Common utility functions:
- `hash_utils.py` - SHA-256 hashing for IDs
- `validators.py` - Email and URL validation
- `file_utils.py` - Excel read/write operations
- `logger.py` - Logging configuration

### Interfaces (`interfaces/`)
Abstract base classes:
- `ServiceInterface` - For Level 3 leaf services
- `CoordinatorInterface` - For Level 1/2 coordinators

### Config (`config/`)
Configuration management:
- `BaseConfig` - YAML config loading
- `env_loader` - .env file loading

## Usage

```python
# Import models
from shared.models import EmailRecord, GradeRecord, FeedbackRecord

# Import utilities
from shared.utils import sha256_hash, validate_email, read_excel

# Import interfaces
from shared.interfaces import ServiceInterface, CoordinatorInterface
```

## Testing

```bash
python -m pytest tests/ -v
```

## Notes

- This module has NO circular dependencies
- All functions have type hints
- All public functions have docstrings

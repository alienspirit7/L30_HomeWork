# Changelog

All notable changes to the Draft Manager module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-11

### Added

#### Core Module
- Initial implementation of DraftManager class
- Orchestration logic for child services (Student Mapper and Draft Composer)
- Email template composition with personalization
- Batch processing support for multiple drafts
- Error handling and graceful degradation

#### Configuration
- `config.yaml` - Main configuration file
- Email template customization (greeting, signature, repo line)
- Logging configuration (level, file path)
- Child service path configuration

#### Documentation
- `README.md` - Comprehensive module documentation
- `PRD.md` - Product Requirements Document
- `QUICKSTART.md` - Quick start guide for rapid setup
- `CHANGELOG.md` - This file
- Inline code documentation and docstrings

#### CLI Interface
- `__main__.py` - Standalone command-line interface
- Support for Excel file inputs (email and feedback records)
- Dry-run mode for testing without creating actual drafts
- Verbose logging option
- JSON and human-readable output formats

#### Package Structure
- `__init__.py` - Package initialization with version info
- `manager.py` - Core DraftManager implementation
- Proper Python package structure for imports

#### Testing
- `tests/test_manager.py` - Comprehensive test suite
- Unit tests for all major functions
- Mock-based testing for child services
- Pytest integration with coverage support
- Test fixtures and sample data

#### Development Tools
- `.gitignore` - Git ignore patterns for Python, credentials, logs
- `requirements.txt` - Python dependencies
- Virtual environment setup instructions
- Logs directory structure

#### Child Services Integration
- Student Mapper service integration
- Draft Composer service integration
- Automatic child service initialization
- Configuration propagation to child services

### Child Services Included

#### Draft Composer (v1.0.0)
- Gmail API integration with OAuth2
- Draft creation as threaded replies
- Configuration via YAML
- Comprehensive documentation

#### Student Mapper (v1.0.0)
- Excel-based email-to-name mapping
- In-memory caching for performance
- Case-insensitive email matching
- Fallback name support
- Sample data generator

### Features

- **Level 2 Task Manager**: Coordinates two Level 3 leaf services
- **Personalization**: Maps email addresses to student names automatically
- **Gmail Integration**: Creates drafts via Gmail API for teacher review
- **Thread Continuity**: Maintains email conversation threading
- **Batch Processing**: Handles multiple email drafts efficiently
- **Error Handling**: Graceful failure handling with detailed reporting
- **Configurable Templates**: Customizable email greeting and signature
- **Standalone Mode**: Can run independently for testing and development

### Technical Details

- **Language**: Python 3.9+
- **Configuration**: YAML-based
- **Logging**: File and console logging with configurable levels
- **Testing**: Pytest with mock support
- **Dependencies**: PyYAML, pandas, openpyxl, google-api-python-client

### Architecture

```
Draft Manager (Level 2)
├── Student Mapper (Level 3 - Leaf)
│   └── Excel data source
└── Draft Composer (Level 3 - Leaf)
    └── Gmail API
```

### API Specification

#### Input
```python
{
    "email_records": List[EmailRecord],
    "feedback_records": List[FeedbackRecord]
}
```

#### Output
```python
{
    "drafts_created": int,
    "drafts_failed": int,
    "draft_details": List[DraftDetail]
}
```

### Known Limitations

- Requires Gmail API OAuth credentials for Draft Composer
- Requires Excel file with student mappings for Student Mapper
- Child services must be configured before first use
- OAuth token requires browser for initial authentication

### Future Enhancements (Planned)

- [ ] Database support for student mappings (in addition to Excel)
- [ ] REST API endpoint for integration
- [ ] Support for multiple email templates
- [ ] Scheduled batch processing
- [ ] Email preview before draft creation
- [ ] Statistics dashboard
- [ ] Multi-language support for email templates
- [ ] Attachment support in drafts
- [ ] Custom field support in templates

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-01-11 | Initial release with full functionality |

---

**Maintained by**: Draft Manager Team
**License**: MIT
**Repository**: [Link to repository]

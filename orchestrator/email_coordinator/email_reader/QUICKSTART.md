# Quick Start Guide - Email Reader Manager

Get up and running with the Email Reader Manager in 5 minutes.

## Prerequisites

- Python 3.9+
- Gmail API credentials (OAuth 2.0)

## 1. Install Dependencies

Run the automated setup script:

```bash
./setup.sh
```

Or install manually:

```bash
# Install email_reader dependencies
pip install -r requirements.txt

# Install gmail_reader dependencies
cd gmail_reader && pip install -r requirements.txt && cd ..

# Install email_parser dependencies
cd email_parser && pip install -r requirements.txt && cd ..
```

## 2. Configure Gmail API

### Get Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable Gmail API
4. Create OAuth 2.0 credentials:
   - Application type: Desktop app
   - Download credentials
5. Save as `gmail_reader/data/credentials/credentials.json`

### Directory Structure

```bash
mkdir -p gmail_reader/data/credentials
# Place your credentials.json here
```

## 3. Test Child Services

### Test Gmail Reader

```bash
cd gmail_reader
python -m pytest tests/ -v
cd ..
```

### Test Email Parser

```bash
cd email_parser
python -m pytest tests/ -v
cd ..
```

## 4. Run Email Reader

Once both child services are tested:

```bash
# Test mode - processes 5 emails
python -m manager --mode test

# Batch mode - processes 50 emails
python -m manager --mode batch

# Full mode - processes all unread emails
python -m manager --mode full
```

## 5. Check Output

The processed emails are saved to:

```bash
cat data/output/file_1_2.xlsx
```

Open in Excel or LibreOffice to view the structured data.

## Troubleshooting

### First Run Authentication

On first run, Gmail Reader will:
1. Open a browser window
2. Ask you to sign in to Google
3. Request permissions to read Gmail
4. Save token to `gmail_reader/data/credentials/token.json`

### Common Issues

**"credentials.json not found"**
- Ensure file is at: `gmail_reader/data/credentials/credentials.json`

**"Invalid grant" error**
- Delete `gmail_reader/data/credentials/token.json`
- Re-run to re-authenticate

**"No emails found"**
- Check your Gmail for unread emails with subject "self check of homework"
- Or modify search query in `config.yaml`

## Next Steps

- Read [README.md](README.md) for detailed documentation
- See [PRD.md](PRD.md) for requirements specification
- Explore [gmail_reader/README.md](gmail_reader/README.md)
- Explore [email_parser/README.md](email_parser/README.md)

## Configuration

Customize behavior in `config.yaml`:

```yaml
modes:
  test:
    batch_size: 5    # Change test batch size
  batch:
    batch_size: 50   # Change batch size

gmail_search:
  query: "subject:(self check of homework) is:unread"  # Customize search
```

## Support

For issues or questions:
- Check logs in `./logs/email_reader.log`
- Review child service logs
- See troubleshooting sections in README files

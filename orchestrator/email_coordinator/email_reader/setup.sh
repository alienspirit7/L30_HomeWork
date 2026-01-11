#!/bin/bash
# Email Reader Manager Setup Script

set -e

echo "=== Email Reader Manager Setup ==="
echo ""

# Install main dependencies
echo "1. Installing email_reader dependencies..."
pip install -r requirements.txt

# Setup gmail_reader
echo ""
echo "2. Setting up gmail_reader..."
cd gmail_reader
pip install -r requirements.txt
cd ..

# Setup email_parser
echo ""
echo "3. Setting up email_parser..."
cd email_parser
pip install -r requirements.txt
cd ..

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Configure Gmail API credentials:"
echo "   - Place credentials.json in gmail_reader/data/credentials/"
echo "   - See gmail_reader/README.md for instructions"
echo ""
echo "2. Test the setup:"
echo "   cd gmail_reader && python -m pytest tests/ -v"
echo "   cd email_parser && python -m pytest tests/ -v"
echo ""
echo "3. Run standalone (once credentials are configured):"
echo "   python -m manager --mode test"
echo ""

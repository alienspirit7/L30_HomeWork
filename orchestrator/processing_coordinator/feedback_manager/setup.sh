#!/bin/bash
# Setup script for Feedback Manager module

set -e

echo "========================================"
echo "Feedback Manager - Setup Script"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 not found"; exit 1; }
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo ""

# Install child service dependencies
echo "Installing style_selector dependencies..."
cd style_selector
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd ..
echo ""

echo "Installing gemini_generator dependencies..."
cd gemini_generator
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd ..
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env and add your GEMINI_API_KEY"
    echo "Get your API key from: https://makersuite.google.com/app/apikey"
fi
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data/input data/output logs
mkdir -p style_selector/logs gemini_generator/logs
echo "Directories created"
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GEMINI_API_KEY"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run health check: python -m feedback_manager --health"
echo "4. Process grades: python -m feedback_manager"
echo ""

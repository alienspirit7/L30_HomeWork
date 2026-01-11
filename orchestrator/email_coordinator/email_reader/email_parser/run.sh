#!/bin/bash
# Email Parser Service - Run Script

# Activate virtual environment and run the parser
PYTHONPATH=. ./venv/bin/python __main__.py "$@"

"""
Processing Coordinator - Main Entry Point
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coordinator import ProcessingCoordinator, main

if __name__ == '__main__':
    sys.exit(main())

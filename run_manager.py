#!/usr/bin/env python3
"""
Launcher script for Blocklist Manager
Run this to start the application
"""

import sys
import os

# Add the blocklist_manager package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'blocklist_manager'))

# Import and run the main application
from blocklist_manager.main import main

if __name__ == "__main__":
    main()

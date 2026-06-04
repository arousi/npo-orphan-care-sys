#!/usr/bin/env python
"""
Kahatayn - Orphan Family Management System
Main entry point for the application.
"""

import sys
import logging
from pathlib import Path

# Setup logging
from config import logger, LOG_LEVEL, LOG_FILE

# Configure root logger
logging.basicConfig(level=LOG_LEVEL)
logger.info("=" * 60)
logger.info("Kahatayn System Starting...")
logger.info(f"Log file: {LOG_FILE}")
logger.info("=" * 60)

# Import and start UI
try:
    from ui.ui_main import main
    main()
except ImportError as e:
    logger.error(f"Import error: {e}")
    print(f"Error: Failed to import required modules. {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Application error: {e}")
    print(f"Error: {e}")
    sys.exit(1)

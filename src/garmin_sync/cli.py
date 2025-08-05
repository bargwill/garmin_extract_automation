#!/usr/bin/env python3
"""
Garmin Connect Data Extraction - Command Line Interface

This module provides the command-line interface and orchestration for the
Garmin Connect data extraction tool. It handles logging setup and delegates
the main workflow to the core business logic module.

Functions:
    setup_logging: Configure basic logging for the application
    main: Main CLI entry point that orchestrates the extraction workflow

Author: Your Name
Date: August 3, 2025
Version: 1.0.0
"""

import sys
import logging
from . import core


def setup_logging():
    """Configure basic logging for the application."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def main():
    """
    Main entry point for the command-line interface.

    Orchestrates the complete data extraction workflow by calling functions
    from the core module in the proper sequence.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Set up logging
    setup_logging()

    try:
        # Load configuration and run extraction
        config = core.Config()
        return core.run_extraction(config)

    except Exception as error:
        print(f"Failed to initialize application: {error}")
        return 1


# Entry point for the script
if __name__ == "__main__":
    sys.exit(main())

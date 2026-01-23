#!/usr/bin/env python3
"""
Convert2MD - PDF to Markdown Converter GUI Application
This is the main entry point for the application.
"""

import sys
import os

# Add the project root to the Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for the application."""
    try:
        from gui.main_gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Error importing GUI module: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while running the application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
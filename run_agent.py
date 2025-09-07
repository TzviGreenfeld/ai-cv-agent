#!/usr/bin/env python
"""
Root-level entry point for running the AI CV Agent.
This allows running the agent from the project root without installing the package.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main function
from ai_cv_agent.main import main

if __name__ == "__main__":
    main()

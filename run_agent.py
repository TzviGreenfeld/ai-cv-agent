import sys
from ai_cv_agent.main import main
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main function

if __name__ == "__main__":
    main()

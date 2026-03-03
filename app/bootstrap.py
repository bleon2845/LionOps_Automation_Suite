from pathlib import Path
import sys

def setup_project_path(current_file: str):
    """
    Adds the project root to sys.path.
    current_file: pass __file__ from the caller
    """
    project_root = Path(current_file).resolve().parent.parent  # .../app -> project root
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


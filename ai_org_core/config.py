from pathlib import Path

# Determine the project root directory dynamically.
# This assumes config.py is in ai_org_core, and the project root is one level up.
PROJECT_ROOT = Path(__file__).parent.parent

# Define key directories relative to the project root.
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
RESULTS_DIR = PROJECT_ROOT / "results"
MEMORY_DIR = WORKSPACE_DIR / "memory"
CUSTOM_TOOLS_DIR = WORKSPACE_DIR / "custom_tools"
UPLOAD_DIR = WORKSPACE_DIR / "uploads"

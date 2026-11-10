from pathlib import Path
import sys

__version__ = "0.1.0"

_CORE_DIR = Path(__file__).resolve().parents[2] / "linhx_core"
if _CORE_DIR.is_dir() and str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

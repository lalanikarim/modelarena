"""Logging setup module."""
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

def _load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def setup_logging():
    cfg = _load_config()
    level = cfg["log_level"]
    file_path = cfg["log_file"]
    return {"level": level, "file": file_path}

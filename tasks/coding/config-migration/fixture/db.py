"""Database connection module."""
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

def _load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def get_connection():
    cfg = _load_config()
    host = cfg["db_host"]
    port = cfg["db_port"]
    name = cfg["db_name"]
    # Simulated connection string
    return f"postgresql://{host}:{port}/{name}"

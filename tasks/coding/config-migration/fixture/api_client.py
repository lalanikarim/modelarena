"""API client module."""
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

def _load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def get_api_client():
    cfg = _load_config()
    key = cfg["api_key"]
    endpoint = cfg["api_endpoint"]
    return {"key": key, "endpoint": endpoint}

import json
from typing import Any, Dict, Optional
from pathlib import Path

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json_file(data: Dict[str, Any], file_path: str):
    """Save data to a JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def ensure_directory(directory: str):
    """Ensure a directory exists, create if it doesn't"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def format_error(error: Exception) -> Dict[str, str]:
    """Format an exception into a dictionary"""
    return {
        "error_type": error.__class__.__name__,
        "error_message": str(error)
    }

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary using dot notation"""
    keys = key.split('.')
    value = data
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k, default)
        else:
            return default
    return value 
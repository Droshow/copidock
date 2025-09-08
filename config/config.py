import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.toml"
DEFAULT_PROFILE = "default"

def load_config(profile: str) -> Dict[str, Any]:
    """Load configuration from TOML file"""
    conf = {"api_base": None, "api_key": None, "timeout_secs": 15}
    
    if not CONFIG_PATH.exists():
        return conf
        
    current_section = None
    for line in CONFIG_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
            
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip()
            continue
            
        if "=" in line and current_section == profile:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            
            if key in ("api_base", "api_key"):
                conf[key] = value
            elif key == "timeout_secs":
                try:
                    conf[key] = int(value)
                except ValueError:
                    pass
                    
    return conf

def find_repo_root() -> Path:
    """Find git repository root"""
    current = Path.cwd()
    for path in [current] + list(current.parents):
        if (path / ".git").exists():
            return path
    return current

def get_state_path(repo_root: Path) -> Path:
    """Get path to state file"""
    state_dir = repo_root / ".copidock"
    state_dir.mkdir(exist_ok=True)
    return state_dir / "state.json"

def load_state(repo_root: Path) -> Dict[str, Any]:
    """Load thread state"""
    state_file = get_state_path(repo_root)
    if state_file.exists():
        try:
            return json.loads(state_file.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}

def save_state(repo_root: Path, data: Dict[str, Any]):
    """Save thread state"""
    state_file = get_state_path(repo_root)
    state_file.write_text(json.dumps(data, indent=2))
import os
import subprocess
from typing import Optional, Tuple, Dict, Any, List
import requests
from rich import print as rprint

# was: from ..config import load_config   (this causes your error)
from ..config.config import load_config

def resolve_api(profile: str, explicit_api: Optional[str]) -> Tuple[str, Optional[str], int]:
    """Resolve API base URL, key, and timeout"""
    # Precedence: flag > env > config > terraform
    if explicit_api:
        return explicit_api.rstrip("/"), None, 15
        
    if os.getenv("COPIDOCK_API"):
        return (
            os.getenv("COPIDOCK_API").rstrip("/"),
            os.getenv("COPIDOCK_API_KEY"),
            15
        )
    
    config = load_config(profile)
    api_base = config.get("api_base")
    
    if not api_base:
        rprint("[red]No API base configured. Set --api, COPIDOCK_API, or ~/.copidock/config.toml[/red]")
        raise RuntimeError("No API configuration found")
        
    return api_base.rstrip("/"), config.get("api_key"), int(config.get("timeout_secs", 15))

class CopidockAPI:
    """API client for Copidock"""
    
    def __init__(self, api_base: str, api_key: Optional[str] = None, timeout: int = 15):
        self.api_base = api_base
        self.api_key = api_key
        self.timeout = timeout
    
    def _headers(self) -> Dict[str, str]:
        headers = {"content-type": "application/json"}
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def create_thread(self, goal: str, repo: str = "", branch: str = "main") -> Dict[str, Any]:
        """Create a new thread"""
        payload = {"goal": goal, "repo": repo, "branch": branch}
        response = requests.post(
            f"{self.api_base}/thread/start",
            headers=self._headers(),
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def create_note(self, content: str, tags: list = None, thread_id: str = "") -> Dict[str, Any]:
        """Create a new note"""
        payload = {
            "content": content,
            "tags": tags or [],
            "thread_id": thread_id
        }
        response = requests.post(
            f"{self.api_base}/notes",
            headers=self._headers(),
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def create_snapshot(self, thread_id: str, paths: list = None, message: str = "") -> Dict[str, Any]:
        """Create a snapshot"""
        payload = {
            "thread_id": thread_id, 
            "paths": paths or [],
            "message": message
        }
        response = requests.post(
            f"{self.api_base}/snapshot",
            headers=self._headers(),
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def get_latest_snapshot(self, thread_id: str) -> Dict[str, Any]:
        """Get latest snapshot for thread"""
        response = requests.get(
            f"{self.api_base}/rehydrate/{thread_id}/latest",
            headers=self._headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def create_comprehensive_snapshot(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive snapshot with synthesized sections"""
        # payload = {
        #     "thread_id": thread_id,
        #     "message": message,
        #     "inline_sources": inline_sources,
        #     "synth": synth_sections
        # }
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dict")
        if not payload.get("thread_id"):
            raise ValueError("payload.thread_id is required")
        if "synth" not in payload:
            raise ValueError("payload.synth is required")
        
        response = requests.post(
            f"{self.api_base}/snapshot/comprehensive",
            headers=self._headers(),
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def create_comprehensive_snapshot_vargs(
        self,
        thread_id: str,
        inline_sources: list,
        synth_sections: Dict[str, Any],
        message: str = "",
        stage: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "thread_id": thread_id,
            "synth": synth_sections,
            "inline_sources": inline_sources or [],
            "message": message,
        }
        if stage: payload["stage"] = stage
        if repo:  payload["repo"]  = repo
        response = requests.post(
            f"{self.api_base}/snapshot/comprehensive",
            headers=self._headers(),
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    # In your api.py file, add this method to the CopidockAPI class:

    def hydrate_snapshot(self, thread_id: str, markdown_content: str, metadata: dict) -> dict:
        """Save comprehensive snapshot markdown to S3 for rehydration"""
        url = f"{self.api_base}/snapshots/{thread_id}/hydrate"
        
        payload = {
            "markdown_content": markdown_content,
            "metadata": metadata
        }
        
        response = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
        
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        return response.json()

    def rehydrate_from_markdown(self, rehydration_id: str) -> dict:
        """Retrieve comprehensive snapshot markdown from S3"""
        url = f"{self.api_base}/snapshots/rehydrate/{rehydration_id}"

        response = requests.get(url, headers=self._headers(), timeout=self.timeout)

        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")

        return response.json()
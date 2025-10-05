# copidock/cli/interactive/__init__.py
"""Interactive CLI components for guided snapshot creation"""

from .detection import auto_detect_context
from .flow import run_interactive_flow, confirm_snapshot_creation

__all__ = ['auto_detect_context', 'run_interactive_flow', 'confirm_snapshot_creation']
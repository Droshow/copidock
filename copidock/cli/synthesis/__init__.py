"""
Synthesis module for generating comprehensive snapshots.
Split by development stage for better organization.
"""

from .base import categorize_files, derive_template_vars
from .initial import generate_initial_stage_snapshot
from .development import generate_development_stage_snapshot
from .analysis import analyze_commit_patterns, mine_open_questions

def generate_comprehensive_snapshot(thread_data, file_paths, recent_commits, repo_root, persona, enhanced_context):
    """Main entry point for comprehensive snapshot generation"""
    from rich import print as rprint
    
    # Handle enhanced context safely
    if enhanced_context is None:
        enhanced_context = {}
    
    # Get stage and template strategy
    stage = enhanced_context.get('stage', 'development')
    
    # DEBUGGING: Print what stage we detected
    rprint(f"[dim]🔍 Detected stage: {stage}[/dim]")
    rprint(f"[dim]🔍 Input persona: {persona}[/dim]")
    
    # Route to appropriate stage handler
    if stage == "initial":
        rprint(f"[dim]→ Using initial stage logic[/dim]")
        from .initial import generate_initial_stage_snapshot
        return generate_initial_stage_snapshot(thread_data, enhanced_context, persona)
    else:
        rprint(f"[dim]→ Using development stage logic[/dim]")
        from .development import generate_development_stage_snapshot
        return generate_development_stage_snapshot(thread_data, file_paths, recent_commits, repo_root, persona, enhanced_context)

__all__ = [
    'generate_comprehensive_snapshot',
    'categorize_files',
    'derive_template_vars',
    'generate_initial_stage_snapshot', 
    'generate_development_stage_snapshot',
    'analyze_commit_patterns',
    'mine_open_questions'
]
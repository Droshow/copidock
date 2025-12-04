"""Domain template loading and management"""

import yaml
from pathlib import Path
from typing import Dict, Optional, List, Any
from rich import print as rprint


def load_domain_template(domain_name: str) -> Optional[Dict[str, Any]]:
    """
    Load a domain template by name.
    
    Args:
        domain_name: Name of the domain (e.g., 'pwa', 'healthcare')
    
    Returns:
        Domain template dictionary or None if not found
    """
    # Find templates directory relative to this file
    templates_dir = Path(__file__).parent.parent / "templates" / "domains"
    template_file = templates_dir / f"{domain_name}.yml"
    
    if not template_file.exists():
        rprint(f"[yellow]Warning: Domain template '{domain_name}' not found[/yellow]")
        return None
    
    try:
        with open(template_file, 'r') as f:
            template = yaml.safe_load(f)
        return template
    except Exception as e:
        rprint(f"[red]Error loading domain template '{domain_name}': {e}[/red]")
        return None


def list_available_domains() -> List[str]:
    """
    List all available domain templates.
    
    Returns:
        List of domain names (without .yml extension)
    """
    templates_dir = Path(__file__).parent.parent / "templates" / "domains"
    
    if not templates_dir.exists():
        return []
    
    domains = []
    for template_file in templates_dir.glob("*.yml"):
        domains.append(template_file.stem)
    
    return sorted(domains)


def get_domain_display_name(domain_name: str) -> str:
    """
    Get the display name for a domain.
    
    Args:
        domain_name: Domain identifier (e.g., 'pwa')
    
    Returns:
        Human-readable display name (e.g., 'Progressive Web App')
    """
    template = load_domain_template(domain_name)
    if template and 'display_name' in template:
        return template['display_name']
    return domain_name.replace('-', ' ').title()


def get_domain_questions(domain_name: str) -> List[Dict[str, str]]:
    """
    Get additional questions for a specific domain.
    
    Args:
        domain_name: Domain identifier
    
    Returns:
        List of question dictionaries with 'prompt', 'help_text', 'key', 'default'
    """
    template = load_domain_template(domain_name)
    if template and 'additional_questions' in template:
        return template['additional_questions']
    return []


def get_domain_synthesis_hints(domain_name: str) -> Dict[str, str]:
    """
    Get synthesis hints for a specific domain.
    
    Args:
        domain_name: Domain identifier
    
    Returns:
        Dictionary of synthesis sections with hints
    """
    template = load_domain_template(domain_name)
    if template and 'synthesis_hints' in template:
        return template['synthesis_hints']
    return {}


def merge_synthesis_hints(base_sections: Dict[str, str], domain_hints: Dict[str, str]) -> Dict[str, str]:
    """
    Merge domain-specific synthesis hints into base sections.
    
    Args:
        base_sections: Base synthesis sections from persona template
        domain_hints: Domain-specific hints to merge in
    
    Returns:
        Merged synthesis sections with proper markdown formatting
    """
    merged = base_sections.copy()
    
    def format_section_header(section_name: str) -> str:
        """Convert section_name to proper markdown header"""
        # Convert snake_case to Title Case
        title = section_name.replace('_', ' ').title()
        return f"## {title}\n\n"
    
    for section_name, hint_content in domain_hints.items():
        if section_name in merged:
            # Append domain hints to existing section
            merged[section_name] += f"\n\n### Domain-Specific Guidance\n\n{hint_content}"
        else:
            # Create new section from domain hints with proper header
            merged[section_name] = format_section_header(section_name) + hint_content
    
    return merged


def display_domain_info(domain_name: str) -> None:
    """
    Display information about a domain template.
    
    Args:
        domain_name: Domain identifier
    """
    template = load_domain_template(domain_name)
    
    if not template:
        return
    
    display_name = template.get('display_name', domain_name)
    description = template.get('description', 'No description available')
    
    rprint(f"\n[bold cyan]🎯 Domain: {display_name}[/bold cyan]")
    rprint(f"[dim]{description}[/dim]\n")
    
    # Show additional questions count
    questions = template.get('additional_questions', [])
    if questions:
        rprint(f"[dim]📋 {len(questions)} domain-specific question(s) will be asked[/dim]")
    
    # Show available synthesis hints
    hints = template.get('synthesis_hints', {})
    if hints:
        hint_sections = ', '.join(hints.keys())
        rprint(f"[dim]💡 Enhanced guidance for: {hint_sections}[/dim]")
    
    rprint()

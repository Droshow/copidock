"""
Common utilities shared across synthesis stages
"""
from typing import List, Dict, Any, Optional
from ...templates.loader import template_loader

def categorize_files(file_paths: List[str]) -> Dict[str, List[str]]:
    """Categorize files by type"""
    categories = {
        "Infrastructure": [],
        "Backend/Lambda": [], 
        "Frontend": [],
        "Configuration": [],
        "Tests": [],
        "Documentation": [],
        "Other": []
    }
    
    for file_path in file_paths:
        path_lower = file_path.lower()
        
        if any(x in path_lower for x in ['infra/', '.tf', '.yml', '.yaml']):
            categories["Infrastructure"].append(file_path)
        elif any(x in path_lower for x in ['lambda/', 'lambdas/', '.py']) and 'test' not in path_lower:
            categories["Backend/Lambda"].append(file_path)
        elif any(x in path_lower for x in ['.js', '.jsx', '.ts', '.tsx', '.vue', '.react']):
            categories["Frontend"].append(file_path)
        elif any(x in path_lower for x in ['config', 'requirements.txt', 'package.json', 'setup.py']):
            categories["Configuration"].append(file_path)
        elif 'test' in path_lower:
            categories["Tests"].append(file_path)
        elif any(x in path_lower for x in ['.md', '.rst', '.txt', 'readme']):
            categories["Documentation"].append(file_path)
        else:
            categories["Other"].append(file_path)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}

def derive_template_vars(thread_data: Dict[str, Any], file_categories: Dict[str, List[str]], 
                        persona: str = "senior-backend-dev", enhanced_context: Optional[Dict] = None) -> Dict[str, Any]:
    """Derive template variables using persona templates"""
    return template_loader.resolve_template_vars(persona, thread_data, file_categories, enhanced_context)

def get_category_impact(category: str, file_count: int) -> str:
    """Get impact indicator for file category"""
    if category == "Infrastructure" and file_count > 0:
        return "🔧" if file_count == 1 else "⚠️"
    elif category == "Backend/Lambda" and file_count > 2:
        return "🚀"
    elif category == "Tests" and file_count > 0:
        return "✅"
    elif file_count > 5:
        return "📦"
    else:
        return ""
# copidock/templates/loader.py
import yaml
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class TemplateLoader:
    def __init__(self):
        self.templates_dir = Path(__file__).parent
        self.personas_dir = self.templates_dir / "personas"
        self.sections_dir = self.templates_dir / "sections"
        
        # Cache loaded personas
        self._persona_cache = {}
    
    def list_personas(self) -> List[str]:
        """List available persona templates"""
        personas = []
        for file_path in self.personas_dir.glob("*.yml"):
            personas.append(file_path.stem)
        return sorted(personas)
    
    def load_persona(self, persona_name: str) -> Dict[str, Any]:
        """Load persona template configuration"""
        if persona_name in self._persona_cache:
            return self._persona_cache[persona_name]
        
        persona_file = self.personas_dir / f"{persona_name}.yml"
        if not persona_file.exists():
            raise ValueError(f"Persona template '{persona_name}' not found")
        
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona_config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in persona '{persona_name}': {e}")
        except Exception as e:
            raise ValueError(f"Error loading persona '{persona_name}': {e}")
        
        self._persona_cache[persona_name] = persona_config
        return persona_config
    
    def resolve_template_vars(self, persona_name: str, thread_data: Dict[str, Any], 
                         file_categories: Dict[str, List[str]], enhanced_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Resolve template variables using persona rules"""
        persona = self.load_persona(persona_name)
        goal = thread_data.get('goal', 'development task')
        
        # Handle enhanced context safely
        if enhanced_context is None:
            enhanced_context = {}
        
        # Base template vars
        template_vars = {
            'goal': goal,
            'repo': thread_data.get('repo', 'project'),
            'branch': thread_data.get('branch', 'main'),
            'persona_name': persona.get('name', 'Developer')
        }
        
        # Find matching rule based on file categories
        template_rules = persona.get('template_rules', {})
        
        # Try to find specific category match (prioritize by importance)
        matched_rule = None
        category_priority = ['Infrastructure', 'Backend/Lambda', 'Frontend', 'Tests', 'Configuration', 'Documentation']
        
        for category in category_priority:
            if category in file_categories and category in template_rules:
                matched_rule = template_rules[category].copy()
                break
        
        # Fall back to default rule
        if not matched_rule:
            matched_rule = template_rules.get('default', {}).copy()
        
        # Apply the matched rule
        template_vars.update(matched_rule)
        
        # Apply goal-specific modifiers
        self._apply_goal_modifiers(template_vars, persona, goal)
        
        # **NEW: Apply enhanced context overrides**
        if enhanced_context.get('focus'):
            template_vars['primary_focus'] = enhanced_context['focus']
        if enhanced_context.get('output'):
            template_vars['expected_outputs'] = enhanced_context['output']
        if enhanced_context.get('constraints'):
            template_vars['constraints'] = enhanced_context['constraints']
        
        # Handle task_list formatting
        if isinstance(template_vars.get('task_list'), list):
            template_vars['task_list'] = '\n'.join(f"- {task}" for task in template_vars['task_list'])
        
        return template_vars
            
    def _apply_goal_modifiers(self, template_vars: Dict[str, Any], persona: Dict[str, Any], goal: str):
            """Apply goal-specific modifiers to template variables"""
            goal_modifiers = persona.get('goal_modifiers', {})
            goal_lower = goal.lower()
            
            for pattern, modifiers in goal_modifiers.items():
                if any(keyword in goal_lower for keyword in pattern.split('|')):
                    for key, value in modifiers.items():
                        if key.endswith('_append'):
                            base_key = key.replace('_append', '')
                            if base_key in template_vars:
                                if isinstance(template_vars[base_key], str):
                                    template_vars[base_key] += value
                                elif isinstance(template_vars[base_key], list) and isinstance(value, list):
                                    template_vars[base_key].extend(value)
                        elif key.endswith('_override'):
                            base_key = key.replace('_override', '')
                            template_vars[base_key] = value
                        else:
                            template_vars[key] = value
    # In copidock/templates/loader.py

    def load_template_with_stage(self, persona: str, stage: str, context: Dict, enhanced_context: Dict) -> str:
        """Load template variant based on project stage"""
        
        # Try stage-specific template first
        stage_specific_persona = f"{persona}-{stage}"
        
        try:
            return self.load_template(stage_specific_persona, context, enhanced_context)
        except:
            # Fallback to default template - no error message for now
            return self.load_template(persona, context, enhanced_context)
    
    def load_template(self, persona: str, context: Dict, enhanced_context: Dict) -> str:
        """Load and render template - simplified for now"""
        
        # For now, return a simple stage-aware template
        stage = enhanced_context.get('stage', 'development')
        focus = enhanced_context.get('focus', 'development tasks')
        
        if stage == "initial":
            return f"""## Stage: {stage.upper()}
Focus: {focus}
This is initial stage guidance - architecture and setup focus.
"""
        elif stage == "maintenance":
            return f"""## Stage: {stage.upper()}
Focus: {focus}
This is maintenance stage guidance - stability and risk management focus.
"""
        else:
            return f"""## Stage: {stage.upper()}
Focus: {focus}
This is development stage guidance - feature development focus.
"""

# Global instance
template_loader = TemplateLoader()
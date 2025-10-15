"""
Git analysis and pattern detection utilities
"""
import re
from typing import List, Dict, Any
from pathlib import Path

def analyze_development_context(file_paths, recent_commits, repo_root):
    """Analyze what type of development work is happening"""
    
    # Analyze file types and patterns
    file_analysis = analyze_file_patterns(file_paths)
    
    # Analyze commit messages for intent
    commit_analysis = analyze_commit_patterns(recent_commits)
    
    # Determine primary work area
    work_area = determine_work_area(file_analysis)
    
    # Assess change impact
    change_impact = assess_change_impact(file_analysis, commit_analysis)
    
    # Generate specific recommendations
    recommendations = generate_development_recommendations(work_area, file_analysis, commit_analysis)
    
    return {
        'work_area': work_area,
        'change_impact': change_impact,
        'file_analysis': file_analysis,
        'commit_analysis': commit_analysis,
        'recommendations': recommendations,
        'risk_areas': identify_risk_areas(work_area, file_analysis)
    }

def analyze_file_patterns(file_paths):
    """Analyze the types of files being modified"""
    patterns = {
        'api': 0,
        'frontend': 0,
        'database': 0,
        'tests': 0,
        'config': 0,
        'docs': 0,
        'other': 0
    }
    
    file_details = []
    
    for file_path in file_paths:
        path_lower = file_path.lower()
        file_type = 'other'
        
        if any(keyword in path_lower for keyword in ['api/', 'endpoints/', 'routes/', 'controllers/']):
            file_type = 'api'
        elif any(keyword in path_lower for keyword in ['frontend/', 'ui/', 'components/', 'views/', '.vue', '.jsx', '.tsx']):
            file_type = 'frontend'  
        elif any(keyword in path_lower for keyword in ['migration', 'schema', 'models/', 'database/']):
            file_type = 'database'
        elif any(keyword in path_lower for keyword in ['test', 'spec', '__tests__']):
            file_type = 'tests'
        elif any(keyword in path_lower for keyword in ['config', 'settings', '.env', 'docker', 'deploy']):
            file_type = 'config'
        elif any(keyword in path_lower for keyword in ['readme', 'docs/', '.md', 'documentation']):
            file_type = 'docs'
        
        patterns[file_type] += 1
        file_details.append({
            'path': file_path,
            'type': file_type
        })
    
    return {
        'patterns': patterns,
        'details': file_details,
        'total_files': len(file_paths)
    }

def analyze_commit_patterns(recent_commits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Enhanced commit analysis with error handling"""
    if not recent_commits:
        return {
            'fix_commits': 0,
            'feature_commits': 0,
            'refactor_commits': 0,
            'test_commits': 0,
            'docs_commits': 0,
            'config_commits': 0,
            'common_words': {},
            'urgency_indicators': [],
            'intent': 'unknown',
            'urgency': 'normal',
            'commit_count': 0,
            'keywords_found': 0
        }
    
    patterns = {
        'fix_commits': 0,
        'feature_commits': 0,
        'refactor_commits': 0,
        'test_commits': 0,
        'docs_commits': 0,
        'config_commits': 0,
        'common_words': {},
        'urgency_indicators': []
    }
    
    urgency_words = ['urgent', 'critical', 'hotfix', 'emergency', 'asap', 'breaking']
    commit_messages = [commit.get('message', '').lower() for commit in recent_commits]
    combined_text = ' '.join(commit_messages)
    
    for commit in recent_commits:
        try:
            subject = commit.get('subject', '').lower()
            if not subject:
                continue
                
            # Categorize commits with better pattern matching
            if any(word in subject for word in ['fix', 'bug', 'error', 'issue', 'resolve']):
                patterns['fix_commits'] += 1
            elif any(word in subject for word in ['feat', 'feature', 'add', 'implement', 'new']):
                patterns['feature_commits'] += 1
            elif any(word in subject for word in ['refactor', 'cleanup', 'improve', 'optimize']):
                patterns['refactor_commits'] += 1
            elif any(word in subject for word in ['test', 'spec', 'coverage', 'unit', 'integration']):
                patterns['test_commits'] += 1
            elif any(word in subject for word in ['doc', 'readme', 'comment', 'documentation']):
                patterns['docs_commits'] += 1
            elif any(word in subject for word in ['config', 'setup', 'env', 'deploy', 'build']):
                patterns['config_commits'] += 1
            
            # Check for urgency with context
            for word in urgency_words:
                if word in subject:
                    patterns['urgency_indicators'].append({
                        'commit': commit.get('hash', 'unknown')[:8],
                        'word': word,
                        'subject': commit.get('subject', 'No subject')
                    })
            
            # Enhanced word counting with better filtering
            stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
            words = re.findall(r'\b\w{3,}\b', subject.lower())
            for word in words:
                if word not in stopwords and len(word) > 2:
                    patterns['common_words'][word] = patterns['common_words'].get(word, 0) + 1
                    
        except Exception as e:
            # Log error but continue processing other commits
            continue
    
    # Detect intent patterns
    intent_patterns = {
        'feature': ['add', 'implement', 'create', 'new'],
        'bugfix': ['fix', 'bug', 'issue', 'resolve', 'correct'],
        'refactor': ['refactor', 'clean', 'improve', 'optimize'],
        'docs': ['docs', 'documentation', 'readme', 'comment'],
        'test': ['test', 'testing', 'spec', 'coverage'],
        'config': ['config', 'setup', 'deploy', 'ci', 'build']
    }
    
    detected_intent = 'general'
    max_matches = 0
    
    for intent, keywords in intent_patterns.items():
        matches = sum(1 for keyword in keywords if keyword in combined_text)
        if matches > max_matches:
            max_matches = matches
            detected_intent = intent
    
    # Detect urgency
    urgency = 'normal'
    urgent_keywords = ['urgent', 'critical', 'hotfix', 'emergency', 'asap']
    if any(keyword in combined_text for keyword in urgent_keywords):
        urgency = 'high'
    
    # Add intent analysis to patterns
    patterns.update({
        'intent': detected_intent,
        'urgency': urgency,
        'commit_count': len(recent_commits),
        'keywords_found': max_matches
    })
    
    return patterns

def determine_work_area(file_analysis):
    """Determine the primary area of development work"""
    patterns = file_analysis['patterns']
    
    # Find the area with the most file changes
    max_files = max(patterns.values())
    if max_files == 0:
        return 'general'
    
    for area, count in patterns.items():
        if count == max_files and area != 'other':
            return area
    
    return 'general'

def assess_change_impact(file_analysis, commit_analysis):
    """Assess the potential impact of changes"""
    file_count = file_analysis['total_files']
    commit_count = commit_analysis['commit_count']
    urgency = commit_analysis['urgency']
    
    if urgency == 'high' or file_count > 10 or commit_count > 5:
        return 'high'
    elif file_count > 5 or commit_count > 3:
        return 'medium'
    else:
        return 'low'

def generate_development_recommendations(work_area, file_analysis, commit_analysis):
    """Generate specific recommendations based on the development context"""
    recommendations = []
    
    intent = commit_analysis['intent']
    
    if work_area == 'api':
        recommendations.extend([
            "Test all modified API endpoints thoroughly",
            "Verify authentication and authorization still work",
            "Update API documentation (OpenAPI/Swagger)",
            "Check for breaking changes in API contracts"
        ])
    
    elif work_area == 'frontend':
        recommendations.extend([
            "Test across different browsers and screen sizes", 
            "Check mobile responsiveness",
            "Verify accessibility compliance",
            "Test user interactions and workflows"
        ])
    
    elif work_area == 'database':
        recommendations.extend([
            "Create reversible database migrations",
            "Test migrations on staging data first",
            "Backup production data before deployment",
            "Monitor query performance impact"
        ])
    
    elif work_area == 'tests':
        recommendations.extend([
            "Run full test suite to ensure no regressions",
            "Check test coverage metrics",
            "Verify tests are not flaky or interdependent",
            "Update test documentation if needed"
        ])
    
    # Add intent-specific recommendations
    if intent == 'feature':
        recommendations.extend([
            "Document the new feature functionality",
            "Add comprehensive tests for the new feature",
            "Consider feature flags for gradual rollout"
        ])
    elif intent == 'bugfix':
        recommendations.extend([
            "Add regression tests to prevent future occurrences",
            "Verify the fix doesn't introduce new issues",
            "Document the root cause and solution"
        ])
    
    return recommendations

def identify_risk_areas(work_area, file_analysis):
    """Identify potential risk areas based on development context"""
    risks = []
    
    if work_area == 'api':
        risks.extend([
            "Breaking API contracts for existing clients",
            "Authentication or authorization bypass",
            "Performance impact on high-traffic endpoints"
        ])
    elif work_area == 'database':
        risks.extend([
            "Data loss during migration",
            "Performance degradation of existing queries",
            "Constraint violations with existing data"
        ])
    elif work_area == 'frontend':
        risks.extend([
            "Cross-browser compatibility issues",
            "Mobile device performance problems",
            "Accessibility regressions"
        ])
    
    # General risks based on file count
    if file_analysis['total_files'] > 5:
        risks.append("High number of file changes increases integration risk")
    
    return risks

def mine_open_questions(file_paths: List[str], repo_root: str, recent_commits: List[Dict[str, Any]]) -> str:
    """Enhanced extraction of TODOs, FIXMEs, and questions from files and commits"""
    
    # Enhanced patterns with context capture
    patterns = {
        'TODO': r'(?:TODO|@todo):?\s*(.{3,100})',
        'FIXME': r'(?:FIXME|@fixme):?\s*(.{3,100})',
        'QUESTION': r'(?:QUESTION|@question|\?{2,}):?\s*(.{3,100})',
        'TBD': r'(?:TBD|@tbd):?\s*(.{3,100})',
        'HACK': r'(?:HACK|@hack):?\s*(.{3,100})',
        'XXX': r'(?:XXX|@xxx):?\s*(.{3,100})',
        'NOTE': r'(?:NOTE|@note):?\s*(.{3,100})',
        'REVIEW': r'(?:REVIEW|@review):?\s*(.{3,100})'
    }
    
    questions_by_type = {ptype: [] for ptype in patterns.keys()}
    
    # Enhanced file scanning with size limits and error handling
    for file_path in file_paths[:15]:  # Reasonable limit
        try:
            full_path = Path(repo_root) / file_path
            if not full_path.exists() or not full_path.is_file():
                continue
                
            # Skip very large files to avoid memory issues
            file_size = full_path.stat().st_size
            if file_size > 2 * 1024 * 1024:  # Skip files > 2MB
                continue
                
            # Safe file reading with encoding fallback
            try:
                content = full_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    content = full_path.read_text(encoding='latin-1', errors='ignore')
                except:
                    continue  # Skip if can't read
                    
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Skip very long lines to avoid regex performance issues
                if len(line) > 200:
                    line = line[:200] + "..."
                    
                for pattern_type, pattern in patterns.items():
                    try:
                        matches = re.findall(pattern, line, re.IGNORECASE)
                        for match in matches:
                            clean_match = match.strip().rstrip('.,;:')
                            if len(clean_match) > 5:  # Filter very short matches
                                questions_by_type[pattern_type].append({
                                    'text': clean_match,
                                    'file': file_path,
                                    'line': line_num,
                                    'context': line.strip()[:80] + ('...' if len(line.strip()) > 80 else '')
                                })
                    except re.error:
                        # Skip malformed regex patterns
                        continue
                        
        except Exception as e:
            # Log but continue with other files
            continue
    
    # Enhanced commit message analysis
    for commit in recent_commits:
        try:
            commit_text = f"{commit.get('subject', '')} {commit.get('body', '')}"
            for pattern_type, pattern in patterns.items():
                try:
                    matches = re.findall(pattern, commit_text, re.IGNORECASE)
                    for match in matches:
                        clean_match = match.strip().rstrip('.,;:')
                        if len(clean_match) > 5:
                            questions_by_type[pattern_type].append({
                                'text': clean_match,
                                'file': f"Commit {commit.get('hash', 'unknown')[:8]}",
                                'line': 0,
                                'context': commit.get('subject', 'No subject')
                            })
                except re.error:
                    continue
        except Exception as e:
            continue
    
    # Format output with better organization
    if not any(questions_by_type.values()):
        return "## Open Questions\n\nNo open questions found in recent changes."
    
    output = ["## Open Questions\n"]
    
    # Prioritize critical question types
    priority_types = ['FIXME', 'TODO', 'QUESTION', 'REVIEW', 'HACK', 'TBD', 'XXX', 'NOTE']
    
    question_count = 0
    total_limit = 12  # Global limit to prevent huge sections
    
    for qtype in priority_types:
        questions = questions_by_type[qtype]
        if questions and question_count < total_limit:
            output.append(f"### {qtype}s\n")
            
            # Sort by file path for better organization
            questions.sort(key=lambda x: x['file'])
            
            type_limit = min(4, total_limit - question_count)  # Max 4 per type
            for q in questions[:type_limit]:
                if question_count >= total_limit:
                    break
                    
                output.append(f"{question_count + 1}. **{q['text']}**")
                output.append(f"   - *{q['file']}:{q['line']}*")
                if q['context'] != q['text'] and q['context'].strip():
                    output.append(f"   - Context: `{q['context']}`")
                output.append("")
                question_count += 1
    
    # Add summary if we hit limits
    total_questions = sum(len(questions) for questions in questions_by_type.values())
    if total_questions > question_count:
        output.append(f"*... and {total_questions - question_count} more questions found*")
    
    return "\n".join(output)
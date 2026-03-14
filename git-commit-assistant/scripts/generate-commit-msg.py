#!/usr/bin/env python3
"""Generate a commit message suggestion from git diff."""

import subprocess
import re
import sys

def get_git_diff(staged=True):
    """Get the git diff output."""
    cmd = ['git', 'diff', '--staged'] if staged else ['git', 'diff']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return None

def analyze_diff(diff_output):
    """Analyze diff to determine commit type and scope."""
    stats = {
        'additions': 0,
        'deletions': 0,
        'files': [],
        'types': set()
    }

    lines = diff_output.split('\n')
    current_file = None

    for line in lines:
        if line.startswith('diff --git'):
            # Extract filename
            match = re.search(r'b/(.*)$', line)
            if match:
                current_file = match.group(1)
                stats['files'].append(current_file)

        elif line.startswith('+') and not line.startswith('+++'):
            stats['additions'] += 1

            # Detect patterns
            if 'def ' in line or 'function ' in line:
                if 'test' in line.lower() or current_file and 'test' in current_file.lower():
                    stats['types'].add('test')
                else:
                    stats['types'].add('feat')

            elif 'fix' in line.lower() or 'bug' in line.lower() or 'patch' in line.lower():
                stats['types'].add('fix')

            elif 'TODO' in line or 'FIXME' in line:
                stats['types'].add('chore')

        elif line.startswith('-') and not line.startswith('---'):
            stats['deletions'] += 1

    return stats

def suggest_commit_message(stats):
    """Generate commit message suggestions."""
    suggestions = []

    # Determine primary type
    if 'fix' in stats['types']:
        commit_type = 'fix'
    elif 'test' in stats['types']:
        commit_type = 'test'
    elif 'feat' in stats['types']:
        commit_type = 'feat'
    else:
        commit_type = 'chore'

    # Determine scope from files
    scopes = set()
    for f in stats['files']:
        if 'test' in f.lower():
            scopes.add('test')
        elif 'doc' in f.lower() or f.endswith('.md'):
            scopes.add('docs')
        elif 'api' in f.lower():
            scopes.add('api')
        elif 'ui' in f.lower() or 'frontend' in f.lower():
            scopes.add('ui')

    scope = list(scopes)[0] if scopes else None

    # Build suggestions
    if len(stats['files']) == 1:
        file_name = stats['files'][0].split('/')[-1] if '/' in stats['files'][0] else stats['files'][0]
        if scope:
            suggestions.append(f"{commit_type}({scope}): update {file_name}")
        else:
            suggestions.append(f"{commit_type}: update {file_name}")
    else:
        action = "add" if stats['additions'] > stats['deletions'] else "update"
        desc = f"{action} multiple files" if len(stats['files']) > 3 else f"{action} {', '.join(stats['files'][:3])}"
        if scope:
            suggestions.append(f"{commit_type}({scope}): {desc}")
        else:
            suggestions.append(f"{commit_type}: {desc}")

    # Add suggestions based on stats
    if stats['additions'] > 100 and stats['deletions'] < 20:
        suggestions.append("feat: add new functionality")

    if stats['deletions'] > stats['additions']:
        suggestions.append("refactor: simplify code structure")

    return suggestions

def main():
    diff = get_git_diff(staged=True)
    if not diff:
        print("No staged changes found. Stage files with 'git add' first.")
        return 1

    stats = analyze_diff(diff)
    suggestions = suggest_commit_message(stats)

    print(f"Files changed: {len(stats['files'])}")
    print(f"Additions: {stats['additions']}")
    print(f"Deletions: {stats['deletions']}")
    print()
    print("Suggested commit messages:")
    for i, msg in enumerate(suggestions, 1):
        print(f"  {i}. {msg}")

    return 0

if __name__ == "__main__":
    sys.exit(main())

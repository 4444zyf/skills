#!/usr/bin/env python3
"""Generate a structured code review summary."""

import sys
import json
from datetime import datetime

def generate_review_summary(findings):
    """Generate a markdown review summary from findings."""

    summary = f"""# Code Review Summary

**Review Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary Statistics

| Category | Count |
|----------|-------|
| Critical | {findings.get('critical', 0)} |
| Warning | {findings.get('warning', 0)} |
| Suggestion | {findings.get('suggestion', 0)} |
| Question | {findings.get('question', 0)} |

## Findings

"""

    for category in ['critical', 'warning', 'suggestion', 'question']:
        items = findings.get(f'{category}_items', [])
        if items:
            summary += f"\n### {category.capitalize()}s\n\n"
            for item in items:
                summary += f"- **{item['file']}** (line {item['line']}): {item['message']}\n"

    return summary

if __name__ == "__main__":
    # Example usage with sample data
    sample_findings = {
        "critical": 1,
        "warning": 2,
        "suggestion": 3,
        "question": 1,
        "critical_items": [
            {"file": "auth.py", "line": 45, "message": "SQL injection vulnerability"}
        ],
        "warning_items": [
            {"file": "api.py", "line": 23, "message": "No input validation"},
            {"file": "utils.py", "line": 56, "message": "Deprecated function usage"}
        ],
        "suggestion_items": [
            {"file": "models.py", "line": 12, "message": "Consider adding type hints"},
            {"file": "views.py", "line": 34, "message": "Function is too long"},
            {"file": "tests.py", "line": 89, "message": "Add more edge case tests"}
        ],
        "question_items": [
            {"file": "config.py", "line": 8, "message": "Is this timeout value intentional?"}
        ]
    }

    print(generate_review_summary(sample_findings))

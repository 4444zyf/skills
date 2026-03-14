# My Claude Skills

This repository contains custom skills for Claude Code.

## Installation

Install individual skills using:

```bash
npx skills add <owner/repo>@<skill-name>
```

Or install all skills:

```bash
npx skills add <owner/repo>
```

## Available Skills

| Skill | Description |
|-------|-------------|
| `code-review-helper` | Conduct thorough code reviews with security and performance checks |
| `git-commit-assistant` | Help write meaningful conventional commit messages |
| `project-analyzer` | Analyze and understand unfamiliar project structures |

## Skill Structure

Each skill follows the standard Claude Code skill format:

```
skill-name/
├── SKILL.md           # Required: Skill definition with YAML frontmatter
├── scripts/           # Optional: Utility scripts
├── references/        # Optional: Reference documentation
└── assets/            # Optional: Templates and assets
```

## Creating a New Skill

1. Create a new directory under `skills/`
2. Add a `SKILL.md` file with proper frontmatter
3. Add any supporting files in `scripts/`, `references/`, or `assets/`

### SKILL.md Template

```markdown
---
name: skill-name
description: This skill should be used when the user asks to "do something specific". Include trigger phrases that activate this skill.
version: 1.0.0
---

# Skill Name

Brief description of what this skill does.

## Instructions

Detailed instructions for Claude on how to use this skill...

## Additional Resources

- `references/guide.md` - Detailed reference guide
- `scripts/helper.py` - Utility script
```

## License

MIT

---
name: project-analyzer
description: This skill should be used when the user asks to "analyze project", "understand codebase", "explore project structure", "analyze architecture", "what does this project do", or needs help understanding an unfamiliar codebase.
version: 1.0.0
---

# Project Analyzer

A skill for quickly analyzing and understanding project structure and architecture.

## When to Use

- Exploring an unfamiliar codebase
- Understanding project architecture
- Identifying tech stack and dependencies
- Finding entry points and main components
- Analyzing project organization

## Analysis Process

### Step 1: Identify Project Type

Look for common indicators:

**Web Projects**
- `package.json` → Node.js/JavaScript project
- `next.config.js` → Next.js
- `vite.config.ts` → Vite
- `webpack.config.js` → Webpack

**Python Projects**
- `pyproject.toml` / `setup.py` / `requirements.txt` → Python
- `Pipfile` → Pipenv
- `poetry.lock` → Poetry

**Other Languages**
- `Cargo.toml` → Rust
- `go.mod` → Go
- `pom.xml` / `build.gradle` → Java
- `Gemfile` → Ruby

### Step 2: Read Key Configuration Files

1. **README.md** - Project overview and setup instructions
2. **CLAUDE.md** - Project-specific guidelines for Claude
3. **.gitignore** - What files are excluded
4. **LICENSE** - Project license

### Step 3: Analyze Directory Structure

```bash
# Show directory tree (top 3 levels)
tree -L 3 -I 'node_modules|__pycache__|.git'

# Or using find
find . -maxdepth 3 -type d | head -50
```

Look for:
- Source code directories (`src/`, `app/`, `lib/`)
- Test directories (`tests/`, `__tests__/`, `spec/`)
- Configuration files
- Documentation

### Step 4: Identify Entry Points

**Common Entry Points by Language**

| Language | Common Entry Points |
|----------|-------------------|
| Python | `main.py`, `app.py`, `__main__.py`, `manage.py` |
| JavaScript/Node | `index.js`, `main.js`, `app.js`, `server.js` |
| TypeScript | `index.ts`, `main.ts`, `app.ts` |
| Go | `main.go` |
| Rust | `src/main.rs`, `src/lib.rs` |
| Java | `src/main/java/**/Main.java` |

### Step 5: Understand Dependencies

**Python**
```bash
cat requirements.txt
cat pyproject.toml
```

**JavaScript/Node**
```bash
cat package.json | jq '.dependencies, .devDependencies'
```

**Go**
```bash
cat go.mod
cat go.sum
```

**Rust**
```bash
cat Cargo.toml
```

## Analysis Checklist

- [ ] Project type identified
- [ ] Programming language(s) identified
- [ ] Framework detected (if any)
- [ ] Entry points found
- [ ] Main source directories identified
- [ ] Test structure understood
- [ ] Build/test commands known
- [ ] Dependencies understood

## Reporting Structure

When reporting analysis results:

### 1. Project Overview

```
Project Name: [name]
Type: [Web App/API/Library/etc.]
Language: [Primary language]
Framework: [Framework name]
```

### 2. Directory Structure

```
src/
├── components/    # UI components
├── utils/         # Utility functions
├── services/      # Business logic
└── types/         # Type definitions
```

### 3. Key Files

| File | Purpose |
|------|---------|
| `main.py` | Application entry point |
| `config.py` | Configuration |
| `models.py` | Data models |

### 4. Dependencies Summary

- **Core**: Framework, ORM, etc.
- **Testing**: Test framework, fixtures
- **Dev**: Linting, formatting, etc.

## Additional Resources

- `references/language-patterns.md` - Language-specific analysis patterns
- `scripts/analyze-deps.py` - Analyze and categorize dependencies

---
name: git-commit-assistant
description: This skill should be used when the user asks to "commit changes", "write commit message", "create a commit", "stage files", or needs help with git commit workflow including writing meaningful commit messages.
version: 1.0.0
---

# Git Commit Assistant

A skill for helping with git commits and writing meaningful commit messages.

## When to Use

- Creating new commits
- Writing commit messages
- Staging files for commit
- Reviewing changes before commit
- Amending commits

## Commit Workflow

### Step 1: Review Changes

Before committing, understand what changed:

```bash
# Check what files were modified
git status

# Review the actual changes
git diff

# For staged changes
git diff --staged
```

### Step 2: Stage Files

Stage files appropriately:

```bash
# Stage specific files
git add <file1> <file2>

# Stage all changes
git add -A

# Stage with patch (interactive)
git add -p
```

### Step 3: Write Commit Message

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, semicolons, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or fixing tests
- **chore**: Build process or auxiliary tool changes

#### Subject Rules

- Use imperative mood ("Add feature" not "Added feature")
- Don't capitalize first letter
- No period at the end
- Keep under 50 characters

#### Body Rules

- Explain WHAT and WHY, not HOW
- Wrap at 72 characters
- Use bullet points for multiple changes

### Step 4: Create Commit

```bash
# Commit with message
git commit -m "feat: add user authentication"

# Commit with detailed message
git commit -m "feat(auth): implement JWT authentication" -m "- Add login endpoint" -m "- Configure JWT middleware"
```

## Analyzing Changes for Commit Message

When examining git diff output:

1. **Identify the type of change**:
   - New functionality → `feat`
   - Bug fix → `fix`
   - Documentation → `docs`
   - Tests → `test`
   - Refactoring → `refactor`

2. **Determine the scope**:
   - What module/component is affected?
   - Examples: `auth`, `api`, `ui`, `db`, `tests`

3. **Write the subject**:
   - Start with a verb
   - Be specific but concise
   - Examples: "add user login", "fix null pointer", "update README"

4. **Add body if needed**:
   - Multiple related changes
   - Breaking changes
   - Complex rationale

## Examples

### Simple Feature

```
feat: add email validation
```

### Feature with Scope

```
feat(auth): implement password reset

- Add /api/auth/reset-password endpoint
- Send reset email via SendGrid
- Add token expiration (24 hours)
```

### Bug Fix

```
fix(api): resolve null pointer in user controller

The user object was null when session expired.
Now returns 401 Unauthorized instead of 500.
```

### Breaking Change

```
feat(api): change user response format

BREAKING CHANGE: User object now includes nested profile
instead of flat structure. Update client code accordingly.
```

## Additional Resources

- `references/conventional-commits.md` - Full conventional commits specification
- `scripts/generate-commit-msg.py` - Generate commit message from diff

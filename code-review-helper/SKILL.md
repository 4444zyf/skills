---
name: code-review-helper
description: This skill should be used when the user asks to "review code", "check this code", "code review", "review my PR", "review pull request", or wants feedback on code quality, patterns, or best practices.
version: 1.0.0
---

# Code Review Helper

A skill for conducting thorough code reviews with actionable feedback.

## When to Use

- Reviewing pull requests or code changes
- Checking code for bugs, security issues, or performance problems
- Ensuring code follows best practices and project conventions
- Providing constructive feedback on code quality

## Review Process

### Step 1: Gather Context

Before reviewing, gather relevant context:

1. Read the PR description or commit message to understand the intent
2. Check if there's a CLAUDE.md or similar project documentation
3. Identify the files that were changed
4. Understand the scope of changes

### Step 2: Analyze Changes

For each changed file, analyze:

1. **Correctness**: Does the code do what it's supposed to do?
2. **Security**: Are there any security vulnerabilities?
3. **Performance**: Are there inefficient patterns or bottlenecks?
4. **Maintainability**: Is the code readable and well-structured?
5. **Testing**: Are there adequate tests?
6. **Documentation**: Is the code appropriately documented?

### Step 3: Provide Feedback

Structure feedback using these categories:

- **Critical**: Must fix before merge (bugs, security issues)
- **Warning**: Should fix (performance, maintainability)
- **Suggestion**: Nice to have (style, refactoring)
- **Question**: Need clarification

## Review Checklist

### General

- [ ] Code follows project conventions
- [ ] No obvious bugs or logic errors
- [ ] Error handling is appropriate
- [ ] No hardcoded secrets or credentials

### Security

- [ ] Input validation is present
- [ ] SQL injection is prevented
- [ ] XSS vulnerabilities are addressed
- [ ] Command injection is prevented
- [ ] No sensitive data in logs

### Performance

- [ ] No N+1 queries
- [ ] Expensive operations are optimized
- [ ] Caching is used appropriately
- [ ] Memory usage is reasonable

### Maintainability

- [ ] Functions are appropriately sized
- [ ] Naming is clear and consistent
- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Comments explain "why", not "what"

## Additional Resources

- `references/security-patterns.md` - Common security patterns and anti-patterns
- `references/performance-guide.md` - Performance review guidelines
- `scripts/generate-review-summary.py` - Generate a review summary

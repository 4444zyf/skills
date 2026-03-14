# Conventional Commits Specification

## Summary

The Conventional Commits specification is a lightweight convention on top of commit messages. It provides an easy set of rules for creating an explicit commit history.

## Commit Message Structure

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types

| Type | Description |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Changes that don't affect code meaning (formatting) |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Code change that improves performance |
| `test` | Adding or correcting tests |
| `chore` | Changes to build process or auxiliary tools |
| `ci` | Changes to CI configuration files |
| `build` | Changes that affect the build system |
| `revert` | Reverts a previous commit |

## Scopes

Scopes provide additional contextual information:

- `auth` - Authentication/authorization
- `api` - API endpoints
- `ui` - User interface
- `db` - Database
- `config` - Configuration
- `deps` - Dependencies

## Examples

### Commit with description and breaking change

```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

### Commit with no body

```
docs: correct spelling of CHANGELOG
```

### Commit with scope

```
feat(lang): add Polish language
```

### Commit with multi-paragraph body

```
fix: prevent racing of requests

Introduce a request id and reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.
```

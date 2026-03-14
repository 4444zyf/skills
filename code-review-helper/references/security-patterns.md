# Security Patterns Reference

## Common Vulnerabilities to Check

### Injection Attacks

**SQL Injection**
```python
# BAD: String concatenation
query = f"SELECT * FROM users WHERE id = {user_id}"

# GOOD: Parameterized queries
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

**Command Injection**
```python
# BAD: User input in shell command
os.system(f"process_file {filename}")

# GOOD: Use subprocess with proper escaping
subprocess.run(["process_file", filename], check=True)
```

### Cross-Site Scripting (XSS)

```javascript
// BAD: InnerHTML with user input
element.innerHTML = userInput;

// GOOD: Text content
element.textContent = userInput;
```

### Path Traversal

```python
# BAD: Unsanitized file paths
open(f"/var/data/{user_filename}")

# GOOD: Validate and sanitize
safe_path = os.path.normpath(user_filename)
if safe_path.startswith("..") or "/" in safe_path:
    raise ValueError("Invalid filename")
```

## Authentication & Authorization

- Check that authentication is enforced on protected routes
- Verify authorization checks before sensitive operations
- Ensure passwords are hashed properly (bcrypt, Argon2)
- Check for session fixation vulnerabilities
- Verify CSRF protection on state-changing operations

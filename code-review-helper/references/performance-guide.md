# Performance Review Guidelines

## Database Performance

### Query Optimization

**N+1 Query Problem**
```python
# BAD: N+1 queries
for user in users:
    orders = get_orders(user.id)  # Query per user

# GOOD: Single query with JOIN
orders = db.query(User).join(Order).all()
```

**Missing Indexes**
- Check for frequent queries on non-indexed columns
- Look for full table scans in logs
- Consider composite indexes for multi-column queries

### Caching

- Identify expensive computations that could be cached
- Check if HTTP responses have appropriate cache headers
- Look for redundant database queries

## Memory Usage

### Common Issues

- Loading entire datasets into memory
- Not closing file handles
- Circular references preventing GC
- Large string concatenations in loops

### Python-Specific

```python
# BAD: List of large objects in memory
results = [process(item) for item in huge_dataset]

# GOOD: Generator for streaming
results = (process(item) for item in huge_dataset)
```

## Frontend Performance

### Bundle Size

- Check for unused dependencies
- Look for duplicate code
- Verify lazy loading is used for large components

### Rendering

- Avoid unnecessary re-renders
- Use virtualization for long lists
- Debounce expensive operations

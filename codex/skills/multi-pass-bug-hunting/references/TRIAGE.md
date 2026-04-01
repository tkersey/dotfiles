# Triage Decision Tree

## Is This Finding Real?

```
Finding reported
       │
       ▼
Code path executes?
       │
    No─┼─Yes
       │    │
       ▼    ▼
FALSE      Guard clause exists?
POSITIVE        │
(dead code)  No─┼─Yes
                │    │
                ▼    ▼
           Validated    FALSE POSITIVE
           elsewhere?   (protected)
                │
             No─┼─Yes
                │    │
                ▼    ▼
           REAL BUG   FALSE POSITIVE
           Fix it!    (cross-file guard)
```

## By Category

### Category 1: Null Safety

```
Null access reported
       │
       ▼
Is value ever null here?
       │
    No─┼─Yes (could be null)
       │    │
       ▼    ▼
FALSE      Add null check
POSITIVE   or optional chaining
```

**Common false positives:**
- Value validated in caller
- Type system guarantees non-null
- Initialization always happens first

### Category 2: Security

```
Security issue reported
       │
       ▼
Is input from user/external?
       │
    No─┼─Yes
       │    │
       ▼    ▼
FALSE      Is it sanitized
POSITIVE   before use?
(internal)      │
             No─┼─Yes
                │    │
                ▼    ▼
           REAL BUG   FALSE POSITIVE
           Fix ASAP!  (sanitized)
```

**Always real bugs:**
- SQL injection with user input
- XSS with unescaped output
- Command injection

### Category 3: Async/Await

```
Missing await reported
       │
       ▼
Is return value used?
       │
    No─┼─Yes
       │    │
       ▼    ▼
Fire-and-   REAL BUG
forget OK?  Add await
       │
    No─┼─Yes
       │    │
       ▼    ▼
REAL BUG   Document
           intention
```

### Category 4: Resource Leaks

```
Resource leak reported
       │
       ▼
Resource explicitly closed?
       │
    No─┼─Yes
       │    │
       ▼    ▼
Scope-based   FALSE POSITIVE
cleanup?      (explicit close)
       │
    No─┼─Yes (RAII, using, with)
       │    │
       ▼    ▼
REAL BUG   FALSE POSITIVE
           (scope cleanup)
```

## Quick Reference

| Finding | Usually Real? | Quick Check |
|---------|---------------|-------------|
| Null deref | 70% | Check caller validates |
| Missing await | 90% | Check if fire-and-forget |
| SQL injection | 95% | Check if parameterized |
| Resource leak | 60% | Check RAII/scope |
| Error swallowed | 80% | Check if intentional |
| Division by zero | 40% | Check if validated |

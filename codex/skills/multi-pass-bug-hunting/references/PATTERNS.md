# Common Bug Patterns

## Pass 1 Patterns (Automated Detection)

### Null Safety Violations

```
Pattern: Optional access without check
Example: user.profile.name  // user.profile may be undefined

Fix: Optional chaining or guard clause
Fixed: user.profile?.name
Fixed: if (!user.profile) return;
```

### Missing Await

```
Pattern: Async call without await
Example: async function save() {
           db.insert(data);  // Missing await
         }

Fix: Add await
Fixed: await db.insert(data);
```

### Resource Leaks

```
Pattern: Open resource never closed
Example: const file = fs.openSync(path);
         // ... use file
         // forgot fs.closeSync(file)

Fix: Use try/finally or RAII
Fixed: try { ... } finally { fs.closeSync(file); }
```

### Error Swallowing

```
Pattern: Catch with no handling
Example: try { riskyOp(); } catch (e) { }

Fix: At minimum log, usually rethrow
Fixed: try { riskyOp(); } catch (e) {
         logger.error('Operation failed', e);
         throw e;
       }
```

---

## Pass 2 Patterns (Fresh Eyes Review)

### Logic Errors

```
Pattern: Off-by-one in loops
Example: for (let i = 0; i <= arr.length; i++)  // <= should be <

Pattern: Inverted condition
Example: if (isValid) throw new Error();  // Logic reversed

Pattern: Missing break in switch
Example: switch(x) { case 1: doA(); case 2: doB(); }  // Falls through
```

### Edge Cases Missed

```
Pattern: Empty array not handled
Example: const first = arr[0];  // Crashes if arr.length === 0

Pattern: Negative numbers not handled
Example: function sqrt(n) { return Math.sqrt(n); }  // NaN for n < 0

Pattern: Unicode not handled
Example: str.length  // Wrong for emoji, use [...str].length
```

### Incomplete Error Handling

```
Pattern: Some paths throw, others return null
Example: function find(id) {
           if (!id) throw new Error();
           if (!cache[id]) return null;  // Inconsistent
         }

Fix: Consistent error handling strategy
```

---

## Pass 3 Patterns (Integration Issues)

### State Mutation

```
Pattern: Shared state modified unexpectedly
Example: const config = defaultConfig;
         config.timeout = 5000;  // Mutates shared default!

Fix: Clone before modifying
Fixed: const config = { ...defaultConfig };
```

### Race Conditions

```
Pattern: Check-then-act without synchronization
Example: if (cache.has(key)) {
           return cache.get(key);  // May have been evicted
         }

Fix: Atomic operations
Fixed: const value = cache.get(key);
       if (value !== undefined) return value;
```

### Circular Dependencies

```
Pattern: Module A imports B, B imports A
Symptom: Undefined at runtime, works in some orders

Fix: Extract shared code to module C
```

---

## AI-Generated Code Patterns

AI code has specific failure modes. Look for these:

### Hallucinated APIs

```
Pattern: Method doesn't exist on the type
Example: response.getBody()  // No such method, it's response.body
Example: array.unique()  // Array doesn't have unique()
```

### Incomplete Error Paths

```
Pattern: Happy path works, errors crash
Example: async function fetch() {
           const res = await api.get();
           return res.data;  // What if res is undefined?
         }
```

### Context Confusion

```
Pattern: Mixed up variable names or function purposes
Example: Function named 'save' but actually deletes
Example: Variable 'user' used where 'profile' was meant
```

### Oversimplified Solutions

```
Pattern: Works for example case, fails for real data
Example: Split on comma (fails if data contains commas)
Example: Parse as int (fails on very large numbers)
```

---

## Security Patterns

Always flag, never suppress without justification:

### Injection

```
SQL: query = "SELECT * FROM users WHERE id = " + userId
Command: exec("rm " + filename)
XSS: element.innerHTML = userInput
```

### Secrets Exposure

```
Pattern: Credentials in code
Example: const password = "hunter2";
Example: API_KEY = "sk-live-..."
```

### Insecure Defaults

```
Pattern: Security disabled by default
Example: { ssl: false }
Example: { validateCerts: false }
Example: CORS: { origin: '*' }
```

---

## Pass Finding Probability

| Pattern | Pass 1 | Pass 2 | Pass 3 |
|---------|--------|--------|--------|
| Null deref | 90% | 10% | - |
| Logic error | 10% | 80% | 10% |
| Edge case | 5% | 85% | 10% |
| Race condition | 20% | 30% | 50% |
| Security | 80% | 15% | 5% |
| Integration | 5% | 20% | 75% |

---

## Pattern Recognition Tips

1. **Similar code → similar bugs**: If you find a bug, search for the same pattern
2. **Error handling paths**: Trace every throw, every catch, every return null
3. **Boundary values**: 0, -1, empty, MAX_INT, unicode
4. **State transitions**: Before/during/after lifecycle
5. **Concurrent access**: Multiple callers, async races

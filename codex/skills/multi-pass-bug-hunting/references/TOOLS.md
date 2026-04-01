# Tool-Specific Commands

## UBS (Ultimate Bug Scanner)

Primary scanner for multi-pass hunting.

### Basic Usage

```bash
# Full scan with detailed output
ubs . --format=jsonl

# Quick scan (surface only)
ubs . --quick

# Staged files only (pre-commit)
ubs --staged

# Fail CI on warnings
ubs . --fail-on-warning

# Compare to baseline
ubs . --comparison=baseline.json
```

### Output Parsing

```bash
# Count by severity
ubs . --format=jsonl | jq -s 'group_by(.severity) | map({(.[0].severity): length}) | add'

# Filter to errors only
ubs . --format=jsonl | jq 'select(.severity == "error")'

# Get unique file paths
ubs . --format=jsonl | jq -r '.file' | sort -u
```

### Suppression

```typescript
// Inline suppression with justification
// ubs:ignore validated-by-caller
const name = user.profile.name;

// Block suppression
/* ubs:ignore-block security-reviewed-2024 */
exec(cmd);
/* ubs:ignore-block-end */
```

---

## Language-Specific Scanners

### Rust: Clippy

```bash
# Standard warnings as errors
cargo clippy -- -D warnings

# All lints (very strict)
cargo clippy -- -W clippy::all -W clippy::pedantic

# Specific lint categories
cargo clippy -- -W clippy::unwrap_used -W clippy::expect_used

# Output as JSON
cargo clippy --message-format=json 2>&1 | jq 'select(.reason == "compiler-message")'

# Fix automatically
cargo clippy --fix
```

**Key Clippy lints for bug hunting:**

```
clippy::unwrap_used     # Potential panic
clippy::expect_used     # Potential panic with message
clippy::manual_ok_or    # Logic error risk
clippy::redundant_else  # Dead code indicator
```

### TypeScript: ESLint

```bash
# Standard scan
npx eslint . --format=json

# Fix auto-fixable
npx eslint . --fix

# Specific rules
npx eslint . --rule 'no-unused-vars: error'

# Cache for speed
npx eslint . --cache

# Only changed files (git)
git diff --name-only | grep '\.tsx\?$' | xargs npx eslint
```

**Key ESLint rules:**

```json
{
  "@typescript-eslint/no-floating-promises": "error",
  "@typescript-eslint/no-misused-promises": "error",
  "@typescript-eslint/strict-boolean-expressions": "warn",
  "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }]
}
```

### Python: Ruff

```bash
# Full scan
ruff check .

# JSON output
ruff check . --output-format=json

# Auto-fix
ruff check . --fix

# Specific rules
ruff check . --select=E,F,B

# Watch mode
ruff check . --watch
```

**Key Ruff rules:**

```
E (Error)      # Syntax/import errors
F (Pyflakes)   # Undefined names, unused imports
B (Bugbear)    # Likely bugs, design problems
S (Security)   # Security issues (bandit)
```

### Go: staticcheck

```bash
# Full scan
staticcheck ./...

# JSON output
staticcheck -f json ./...

# Specific checks
staticcheck -checks="SA*" ./...
```

### Bash: ShellCheck

```bash
# Single file
shellcheck script.sh

# All scripts
find . -name "*.sh" -exec shellcheck {} \;

# JSON output
shellcheck --format=json script.sh

# Specific severity
shellcheck --severity=warning script.sh
```

---

## Test Runners

### Rust

```bash
# Run all tests
cargo test --all

# With output
cargo test --all -- --nocapture

# Specific test
cargo test test_name

# Watch mode
cargo watch -x test
```

### TypeScript/JavaScript

```bash
# Vitest
bun run test
bun run test:watch
bun run test -- --coverage

# Jest
npm test
npm test -- --coverage
npm test -- --testPathPattern="foo"
```

### Python

```bash
# pytest
pytest -v
pytest --cov=src
pytest -x  # Stop on first failure
```

---

## Git Integration

### Files Changed

```bash
# Since last commit
git diff --name-only HEAD~1

# Staged files
git diff --cached --name-only

# Between branches
git diff --name-only main...HEAD

# Filter by type
git diff --name-only HEAD~1 | grep '\.rs$'
```

### Review Changes

```bash
# Summary of changes
git diff --stat HEAD~1

# First 200 lines of diff
git diff HEAD~1 | head -200

# Specific file
git diff HEAD~1 -- src/main.rs
```

---

## Combined Workflows

### Pre-Commit Check

```bash
#!/bin/bash
set -e

echo "=== Staged files ==="
git diff --cached --name-only

echo "=== UBS scan ==="
ubs --staged --fail-on-warning

echo "=== Lint ==="
npm run lint

echo "=== Tests ==="
npm test
```

### Full Pass Sequence

```bash
#!/bin/bash

echo "=== Pass 1: Automated Scan ==="
ubs . --format=jsonl > pass1.jsonl
echo "Findings: $(wc -l < pass1.jsonl)"

echo "=== Pass 2: Files to review ==="
git diff --name-only HEAD~1

echo "=== Pass 3: Test Suite ==="
cargo test --all && npm test

echo "=== Pass 4: Final Check ==="
ubs . --fail-on-warning
echo "Clean!"
```

---

## CI Configuration

### GitHub Actions

```yaml
- name: UBS Scan
  run: ubs . --fail-on-warning

- name: Clippy
  run: cargo clippy -- -D warnings

- name: ESLint
  run: npm run lint

- name: Tests
  run: npm test
```

### Common CI Flags

```bash
# Non-interactive
CI=true npm test
CARGO_TERM_COLOR=always cargo test

# Fail fast
npm test -- --bail
cargo test -- --test-threads=1

# Coverage
npm test -- --coverage --coverageReporters="text-summary"
```

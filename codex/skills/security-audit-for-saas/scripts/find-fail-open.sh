#!/usr/bin/env bash
# find-fail-open.sh
#
# Grep for common fail-open patterns in TypeScript/JavaScript code.
# Each hit should be reviewed — some are legitimate, some are CRITICAL bugs.
#
# Exit 0 = no suspicious patterns
# Exit 1 = suspicious patterns found (require review)

set -u

REPO_ROOT="${1:-.}"
FINDINGS=0

echo "=== Fail-Open Pattern Scan: $REPO_ROOT ==="
echo

# Pattern 1: catch block returning true/allowed
echo "--- Pattern 1: catch { return true } ---"
matches=$(grep -rnE 'catch[^{]*\{[^}]*return\s+(true|\{[^}]*allowed:\s*true)' "$REPO_ROOT" \
  --include="*.ts" --include="*.tsx" \
  --exclude-dir=node_modules --exclude-dir=.next 2>/dev/null || true)
if [ -n "$matches" ]; then
  echo "⚠ Review these fail-open catches:"
  echo "$matches" | head -20
  FINDINGS=$((FINDINGS + 1))
fi

# Pattern 2: || true or ?? true on permission checks
echo
echo "--- Pattern 2: || true / ?? true ---"
matches=$(grep -rnE '\|\|\s*true\b|\?\?\s*true\b' "$REPO_ROOT" \
  --include="*.ts" --include="*.tsx" \
  --exclude-dir=node_modules --exclude-dir=.next 2>/dev/null || true)
if [ -n "$matches" ]; then
  echo "⚠ Review these default-to-true expressions:"
  echo "$matches" | head -15
  FINDINGS=$((FINDINGS + 1))
fi

# Pattern 3: jwt.decode without verify
echo
echo "--- Pattern 3: jwt.decode() without verify ---"
matches=$(grep -rnE 'jwt\.decode\(' "$REPO_ROOT" \
  --include="*.ts" --include="*.tsx" \
  --exclude-dir=node_modules --exclude-dir=.next 2>/dev/null || true)
if [ -n "$matches" ]; then
  echo "✗ jwt.decode() usage (should use jwt.verify()):"
  echo "$matches"
  FINDINGS=$((FINDINGS + 1))
fi

# Pattern 4: auth checks with fallback
echo
echo "--- Pattern 4: Auth checks with fallback ---"
matches=$(grep -rnE '(canAccess|isAllowed|hasPermission|requireAuth|isAuthenticated)[^{]*\{[^}]*catch' "$REPO_ROOT" \
  --include="*.ts" --include="*.tsx" \
  --exclude-dir=node_modules --exclude-dir=.next 2>/dev/null || true)
if [ -n "$matches" ]; then
  echo "⚠ Auth functions with try-catch (verify they fail-closed):"
  echo "$matches" | head -10
  FINDINGS=$((FINDINGS + 1))
fi

# Pattern 5: Redis catches (rate limit fail-open risk)
echo
echo "--- Pattern 5: Redis error handling ---"
matches=$(grep -rnE 'redis\.[a-z]+\([^)]*\)[^;]*\.catch|await\s+redis\.[a-z]+' "$REPO_ROOT" \
  --include="*.ts" --include="*.tsx" \
  --exclude-dir=node_modules --exclude-dir=.next -A 2 2>/dev/null | grep -B 1 'return true\|allowed: true' || true)
if [ -n "$matches" ]; then
  echo "⚠ Redis error handlers that return true:"
  echo "$matches" | head -15
  FINDINGS=$((FINDINGS + 1))
fi

# Pattern 6: Switch/match with default allow
echo
echo "--- Pattern 6: Switch default allow ---"
matches=$(grep -rnE 'default:[^}]*return\s+true' "$REPO_ROOT" \
  --include="*.ts" --include="*.tsx" \
  --exclude-dir=node_modules --exclude-dir=.next 2>/dev/null || true)
if [ -n "$matches" ]; then
  echo "⚠ Default case returning true (should be deny):"
  echo "$matches" | head -10
  FINDINGS=$((FINDINGS + 1))
fi

# Pattern 7: passthrough() on Zod schemas
echo
echo "--- Pattern 7: Zod passthrough (mass assignment risk) ---"
matches=$(grep -rnE '\.passthrough\(\)' "$REPO_ROOT" \
  --include="*.ts" --include="*.tsx" \
  --exclude-dir=node_modules --exclude-dir=.next 2>/dev/null || true)
if [ -n "$matches" ]; then
  echo "⚠ Zod .passthrough() — verify no mass assignment:"
  echo "$matches"
  FINDINGS=$((FINDINGS + 1))
fi

# Pattern 8: 'as string' casts on external objects
echo
echo "--- Pattern 8: 'as string' casts (Stripe type safety) ---"
matches=$(grep -rnE '\.(customer|subscription|payment_method|price|product)\s+as\s+string' "$REPO_ROOT" \
  --include="*.ts" --include="*.tsx" \
  --exclude-dir=node_modules --exclude-dir=.next 2>/dev/null || true)
if [ -n "$matches" ]; then
  echo "⚠ Unsafe 'as string' casts on Stripe-like objects:"
  echo "$matches" | head -15
  FINDINGS=$((FINDINGS + 1))
fi

echo
echo "=== Summary ==="
if [ "$FINDINGS" -eq 0 ]; then
  echo "✓ No fail-open patterns found"
  exit 0
else
  echo "⚠ $FINDINGS pattern categories require review"
  exit 1
fi

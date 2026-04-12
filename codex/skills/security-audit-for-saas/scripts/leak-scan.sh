#!/usr/bin/env bash
# leak-scan.sh
#
# Quick secret scan for SaaS applications. Catches:
# - Hardcoded API keys in source
# - Secrets in env files committed to git
# - NEXT_PUBLIC_* variables that look like secrets
# - Direct process.env reads outside env.ts
#
# Exit 0 = clean
# Exit >0 = findings

set -u

REPO_ROOT="${1:-.}"
FINDINGS=0

echo "=== Secret Scan: $REPO_ROOT ==="
echo

# 1. Hardcoded secret patterns
echo "--- Check 1: Hardcoded secrets ---"
PATTERNS=(
  "sk_live_[a-zA-Z0-9]{24,}"        # Stripe live secret
  "sk_test_[a-zA-Z0-9]{24,}"        # Stripe test secret (still a concern in prod code)
  "whsec_[a-zA-Z0-9]{24,}"          # Stripe webhook secret
  "rk_live_[a-zA-Z0-9]{24,}"        # Stripe restricted key
  "AKIA[0-9A-Z]{16}"                # AWS access key
  "ghp_[a-zA-Z0-9]{36}"             # GitHub personal access token
  "ghs_[a-zA-Z0-9]{36}"             # GitHub server token
  "github_pat_[a-zA-Z0-9_]{82}"     # GitHub fine-grained PAT
  "xox[baprs]-[a-zA-Z0-9-]{10,}"    # Slack tokens
  "re_[a-zA-Z0-9]{24,}"             # Resend API key
  "phc_[a-zA-Z0-9]{40,}"            # PostHog API key (if exposed)
)

for pattern in "${PATTERNS[@]}"; do
  matches=$(grep -rnE "$pattern" "$REPO_ROOT" \
    --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
    --include="*.py" --include="*.go" --include="*.rs" \
    --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=target \
    --exclude-dir=.git 2>/dev/null || true)
  if [ -n "$matches" ]; then
    echo "✗ Found pattern: $pattern"
    echo "$matches" | head -5
    FINDINGS=$((FINDINGS + 1))
  fi
done

# 2. Env files in git
echo
echo "--- Check 2: Env files committed to git ---"
if [ -d "$REPO_ROOT/.git" ]; then
  if committed_files=$(cd "$REPO_ROOT" && git ls-files 2>/dev/null); then
    committed_env=$(printf '%s\n' "$committed_files" | grep -E '^\.env($|\.)' | grep -v '\.example$' || true)
    if [ -n "$committed_env" ]; then
      echo "✗ Env files tracked in git:"
      echo "$committed_env"
      FINDINGS=$((FINDINGS + 1))
    else
      echo "✓ No env files in git"
    fi
  else
    echo "⚠ Could not inspect tracked files with git ls-files"
    FINDINGS=$((FINDINGS + 1))
  fi
fi

# 3. NEXT_PUBLIC_* variables that look like secrets
echo
echo "--- Check 3: NEXT_PUBLIC_* variables suspicious for secrets ---"
suspicious=$(
  grep -rnE 'NEXT_PUBLIC_[A-Z_]*(SECRET|PRIVATE|KEY)' "$REPO_ROOT" \
    --include="*.ts" --include="*.tsx" --include="*.js" \
    --exclude-dir=node_modules --exclude-dir=.next 2>/dev/null \
    | grep -vE 'NEXT_PUBLIC_[A-Z_]*(SECRET|PRIVATE|KEY)_(ID|NAME|ALGORITHM|PREFIX)\b' \
    || true
)
if [ -n "$suspicious" ]; then
  echo "⚠ NEXT_PUBLIC_* variables with suspicious names:"
  echo "$suspicious"
  FINDINGS=$((FINDINGS + 1))
else
  echo "✓ No suspicious NEXT_PUBLIC_* variables"
fi

# 4. Direct process.env outside env.ts
echo
echo "--- Check 4: Direct process.env outside env.ts ---"
direct_env=$(grep -rn 'process\.env\.' "$REPO_ROOT" \
  --include="*.ts" --include="*.tsx" \
  --exclude-dir=node_modules --exclude-dir=.next \
  | grep -vE 'env\.(ts|js)|\.test\.|\.spec\.' \
  | grep -vE 'NODE_ENV|VERCEL_ENV' || true)
direct_env_count=$(printf '%s\n' "$direct_env" | awk 'NF{count++} END {print count + 0}')
if [ "$direct_env_count" -gt 0 ]; then
  echo "⚠ Found $direct_env_count direct process.env references outside env.ts"
  echo "$direct_env" | head -10
  FINDINGS=$((FINDINGS + 1))
else
  echo "✓ All env access via env.ts"
fi

# 5. Git history scan
echo
echo "--- Check 5: Git history for previously-committed secrets ---"
if [ -d "$REPO_ROOT/.git" ]; then
  if history_paths=$(cd "$REPO_ROOT" && git log --all --full-history --pretty=format: --name-only --diff-filter=A 2>/dev/null); then
    history_secrets=$(printf '%s\n' "$history_paths" | grep -E '^\.env($|\.)' | grep -v '\.example$' | sort -u || true)
    if [ -n "$history_secrets" ]; then
      echo "⚠ Env files found in git history (may need purge):"
      echo "$history_secrets"
      FINDINGS=$((FINDINGS + 1))
    else
      echo "✓ No env files in git history"
    fi
  else
    echo "⚠ Could not inspect git history"
    FINDINGS=$((FINDINGS + 1))
  fi
fi

# 6. Build output secret scan (if .next exists)
echo
echo "--- Check 6: Client bundle secret scan ---"
if [ -d "$REPO_ROOT/.next" ]; then
  bundle_secrets=$(grep -rE 'sk_live_|sk_test_|whsec_' "$REPO_ROOT/.next" 2>/dev/null || true)
  if [ -n "$bundle_secrets" ]; then
    echo "✗ CRITICAL: Secrets in client bundle!"
    echo "$bundle_secrets" | head -5
    FINDINGS=$((FINDINGS + 10))  # Critical weight
  else
    echo "✓ No secrets in .next/ build output"
  fi
else
  echo "⊘ Skipped (no .next/ directory)"
fi

echo
echo "=== Summary ==="
if [ "$FINDINGS" -eq 0 ]; then
  echo "✓ Clean — no findings"
  exit 0
else
  echo "✗ $FINDINGS findings"
  exit 1
fi

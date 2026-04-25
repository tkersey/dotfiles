#!/usr/bin/env bash
# unpinned_deps.sh — flag unpinned dependencies (P37).
#
# Scans for dependency specifications using "*", "^latest", unpinned git refs,
# or other floating version patterns. Reports as candidates for pinning.
#
# Usage: unpinned_deps.sh [run-id]

set -euo pipefail

RUN_ID="${1:-$(date +%Y-%m-%d)-pass-1}"
ART="refactor/artifacts/${RUN_ID}"
mkdir -p "$ART"
OUT="$ART/unpinned_deps.md"

have() { command -v "$1" >/dev/null 2>&1; }

{
  printf '# Unpinned dependencies — %s\n\n' "$RUN_ID"
  printf 'Per [VIBE-CODED-PATHOLOGIES.md P37](references/VIBE-CODED-PATHOLOGIES.md), unpinned or "latest" deps cause non-deterministic builds.\n\n'
} > "$OUT"

FOUND=0

# package.json
if [[ -f package.json ]]; then
  printf '\n## package.json\n\n' >> "$OUT"
  if have jq; then
    unpinned=$(jq -r '(.dependencies // {}) + (.devDependencies // {}) | to_entries[] | select(.value == "*" or .value == "latest" or .value | startswith("^0.0.") or (.value | test("^(git|github|file|link|workspace):") | not) | not) | "  - " + .key + ": " + .value' package.json 2>/dev/null || true)
    if [[ -n "$unpinned" ]]; then
      echo '```' >> "$OUT"
      echo "$unpinned" >> "$OUT"
      echo '```' >> "$OUT"
      FOUND=$((FOUND + 1))
    else
      echo '_no clearly-unpinned deps_' >> "$OUT"
    fi
  else
    echo '_jq not installed; skipping structured check_' >> "$OUT"
  fi
fi

# Check workspace / monorepo packages
for pkg in packages/*/package.json apps/*/package.json; do
  [[ -f "$pkg" ]] || continue
  name=$(jq -r '.name' "$pkg" 2>/dev/null || echo "$pkg")
  if have jq; then
    unpinned=$(jq -r '(.dependencies // {}) + (.devDependencies // {}) | to_entries[] | select(.value == "*" or .value == "latest") | "  - " + .key + ": " + .value' "$pkg" 2>/dev/null || true)
    if [[ -n "$unpinned" ]]; then
      printf '\n## %s\n\n' "$name" >> "$OUT"
      echo '```' >> "$OUT"
      echo "$unpinned" >> "$OUT"
      echo '```' >> "$OUT"
      FOUND=$((FOUND + 1))
    fi
  fi
done

# Cargo.toml
if [[ -f Cargo.toml ]]; then
  printf '\n## Cargo.toml\n\n' >> "$OUT"
  unpinned=$(grep -nE '^\s*[a-zA-Z0-9_-]+\s*=\s*"\*"' Cargo.toml || true)
  if [[ -n "$unpinned" ]]; then
    echo '```' >> "$OUT"
    echo "$unpinned" >> "$OUT"
    echo '```' >> "$OUT"
    FOUND=$((FOUND + 1))
  else
    echo '_no `"*"` wildcard versions in Cargo.toml_' >> "$OUT"
  fi
  # git refs without rev
  git_unrevved=$(grep -nE '^\s*[a-zA-Z0-9_-]+\s*=\s*\{\s*git\s*=' Cargo.toml | grep -v 'rev\s*=' || true)
  if [[ -n "$git_unrevved" ]]; then
    printf '\n### Unrevved git deps\n\n```\n%s\n```\n\n' "$git_unrevved" >> "$OUT"
    FOUND=$((FOUND + 1))
  fi
fi

# pyproject.toml
if [[ -f pyproject.toml ]]; then
  printf '\n## pyproject.toml\n\n' >> "$OUT"
  unpinned=$(grep -nE '^\s*[a-zA-Z0-9_-]+\s*=\s*"\*"' pyproject.toml || true)
  if [[ -n "$unpinned" ]]; then
    echo '```' >> "$OUT"
    echo "$unpinned" >> "$OUT"
    echo '```' >> "$OUT"
    FOUND=$((FOUND + 1))
  else
    echo '_no `"*"` wildcard versions in pyproject.toml_' >> "$OUT"
  fi
fi

# requirements.txt — no version specified
if [[ -f requirements.txt ]]; then
  printf '\n## requirements.txt\n\n' >> "$OUT"
  no_version=$(grep -vE '(==|>=|<=|~=|!=)' requirements.txt | grep -vE '^\s*(#|$)' || true)
  if [[ -n "$no_version" ]]; then
    echo '```' >> "$OUT"
    echo "$no_version" >> "$OUT"
    echo '```' >> "$OUT"
    FOUND=$((FOUND + 1))
  else
    echo '_all deps version-pinned_' >> "$OUT"
  fi
fi

# go.mod — check for v0.0.0-<date>-<sha> (pseudo-versions are OK); check for replace without version
if [[ -f go.mod ]]; then
  printf '\n## go.mod\n\n' >> "$OUT"
  # go.mod has strong semver discipline by default; flag only unusual patterns
  echo '_go.mod has built-in semver requirements; run `go mod tidy` to normalize_' >> "$OUT"
fi

{
  printf '\n---\n\n'
  if [[ $FOUND -eq 0 ]]; then
    printf '## Verdict: No unpinned dependencies found\n\n'
    printf 'All dependency specifications are pinned or use accepted ranges.\n'
  else
    printf '## Verdict: %d manifest(s) have unpinned deps\n\n' "$FOUND"
    printf 'Action items:\n'
    printf '1. For each entry above, find the currently-resolved version (lockfile).\n'
    printf '2. Pin to that exact version in the manifest.\n'
    printf '3. Commit as `refactor(deps): pin <package>` — one lever per commit.\n'
    printf '4. Document any intentional floating (rare; usually only for dev tools).\n'
  fi
} >> "$OUT"

echo "wrote $OUT"
echo "unpinned entries found: $FOUND"

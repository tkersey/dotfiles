#!/usr/bin/env bash
set -euo pipefail

# Lightweight helper for Codex/humans.
# Prints changed files and simple ripgrep search hints for blast-radius review.
# Usage: ./scripts/changed-files-blast-radius.sh [base_ref]
# Default base_ref: origin/main

BASE_REF="${1:-origin/main}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository." >&2
  exit 1
fi

echo "# Changed files vs ${BASE_REF}"
git diff --name-only "${BASE_REF}" || true

echo

echo "# Candidate public contracts touched"
git diff --name-only "${BASE_REF}" | grep -E '(api|schema|migration|routes?|controllers?|models?|proto|openapi|graphql|auth|billing|payment|worker|queue|cron|config|terraform|helm|k8s|package.json|pyproject.toml|Cargo.toml|go.mod)' || true

echo

echo "# Suggested next steps"
echo "1. For each changed exported symbol, search direct references with rg or language tooling."
echo "2. Check tests adjacent to each changed file."
echo "3. Check schemas, migrations, queues, cron, auth, billing, cache, and observability surfaces."
echo "4. Record unknown tacit constraints in the Verification Gap Report."

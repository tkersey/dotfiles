#!/usr/bin/env bash
# api-auth-mapper.sh
#
# Map every API route to its authentication/authorization mechanism.
# Output a table showing which routes use which auth pattern.
# Useful for: finding routes with NO auth, finding inconsistencies, audit reports.
#
# Usage: ./api-auth-mapper.sh [repo-root]

set -euo pipefail

REPO_ROOT="${1:-.}"
API_DIR="$REPO_ROOT/src/app/api"

if [ ! -d "$API_DIR" ]; then
  echo "✗ No API directory found at $API_DIR"
  exit 1
fi

echo "=== API Route Auth Mapping: $API_DIR ==="
echo
printf '%-60s %-30s %-20s\n' "ROUTE" "AUTH MECHANISM" "NOTES"
printf '%-60s %-30s %-20s\n' "-----" "---------------" "-----"

append_note() {
  local existing="$1"
  local addition="$2"
  if [ -n "$existing" ]; then
    printf '%s %s' "$existing" "$addition"
  else
    printf '%s' "$addition"
  fi
}

# Find all route files
find "$API_DIR" -name 'route.ts' -type f | sort | while read -r file; do
  # Derive route path from file path
  route="${file#"$API_DIR"}"
  route="${route%/route.ts}"
  [ -z "$route" ] && route="/"

  # Detect auth mechanism
  auth="UNKNOWN"
  notes=""

  if grep -Eq 'requireAdmin' "$file"; then
    auth="requireAdmin"
  elif grep -Eq 'requireOrgRole|requireOrgPermission' "$file"; then
    auth="requireOrgRole"
  elif grep -Eq 'requireSubscription' "$file"; then
    auth="requireSubscription"
  elif grep -Eq 'requireAuth|requireUser' "$file"; then
    auth="requireAuth"
  elif grep -Eq 'verifyWebhookSignature|constructEvent|verify-webhook-signature' "$file"; then
    auth="webhook-signature"
  elif grep -Eq 'verifyCronAuth|CRON_SECRET' "$file"; then
    auth="cron-secret"
  elif grep -Eq 'trackAbuseSignal|rateLimit' "$file" && ! grep -Eq 'requireAuth|getUser' "$file"; then
    auth="rate-limit-only"
    notes="PUBLIC"
  else
    auth="NONE?"
    notes="REVIEW"
  fi

  # CSRF notes
  if grep -Eq 'validateCsrf|csrfExempt' "$file"; then
    notes="$(append_note "$notes" "csrf-handled")"
  fi

  printf '%-60s %-30s %-20s\n' "$route" "$auth" "$notes"
done

echo
echo "=== Summary ==="
echo "Review any route marked 'NONE?' or 'REVIEW'"
echo "Verify public endpoints are intentional"
echo "Cross-check against references/API-SECURITY.md"

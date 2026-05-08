#!/usr/bin/env bash
# scripts/install-referenced-skills.sh — Bulk-install missing referenced skills via jsm.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/install-referenced-skills.sh <audit-dir>

Reads <audit-dir>/phase0_skill_inventory.json (produced by check-skills.sh)
and runs `jsm install` for every skill marked .present=false. If jsm is not
installed or not authenticated, prints the fix-it next-step to stderr and
exits 0 (advisory).

Args:
  <audit-dir>   Path to the audit/ directory inside the sibling workspace.

Exit codes:
  0  Installs attempted (or jsm missing — advisory).
  2  Missing arguments, or inventory file not found (run check-skills.sh
     first to produce one).

Example:
  scripts/install-referenced-skills.sh /path/to/__audit/audit
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

AUDIT_DIR="$1"
INVENTORY="$AUDIT_DIR/phase0_skill_inventory.json"

if [ ! -f "$INVENTORY" ]; then
  echo "no inventory at $INVENTORY; run check-skills.sh first" >&2
  exit 2
fi

if ! command -v jsm >/dev/null 2>&1; then
  echo "jsm not installed; cannot bulk-install. See SKILL-FALLBACKS.md." >&2
  echo "To install jsm: curl -fsSL https://jeffreys-skills.md/install.sh | bash"
  exit 0
fi

if ! jsm whoami >/dev/null 2>&1; then
  echo "jsm not authenticated; run: jsm login" >&2
  exit 0
fi

# Extract missing skill names
missing=$(jq -r '.skills | to_entries | map(select(.value.present == false)) | .[].key' "$INVENTORY")

if [ -z "$missing" ]; then
  echo "no missing skills"
  exit 0
fi

echo "installing missing skills via jsm:"
echo "$missing"

for skill in $missing; do
  echo "  jsm install $skill ..."
  jsm install "$skill" || echo "    (failed — note in HANDOFF.md)"
done

echo "install complete; re-run check-skills.sh to update inventory"
exit 0

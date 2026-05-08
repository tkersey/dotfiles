#!/usr/bin/env bash
# tools/compute_surface_id.sh — Compute a deterministic surface_id from descriptors.
# Format: <kind>__<subtree-segment?>__<name-segment>
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/compute_surface_id.sh <kind> [<subtree>] <name>

Computes a deterministic surface_id from a (kind, subtree, name) triple.
The same triple always yields the same ID, which is what makes cumulative
cross-pass scoring possible.

Args:
  <kind>      Surface kind prefix. Core kinds: verb | flag | env | exit |
              error | config | signal | prompt | subcommand_path. Extension
              kinds such as mcp_tool are allowed when file-stem-safe.
  [<subtree>] The subcommand path the surface lives under (e.g. "list",
              "auth login"). Use "" or omit for surfaces that span subtrees.
  <name>      The name (e.g. "list", "--json", "MYTOOL_HOME", "1").

Output:
  One line on stdout: <kind>__<subtree-segment?>__<name-segment>

Each segment after <kind> is file-stem-safe. If a raw segment must be
normalized, a short content hash is appended so distinct descriptors such as
"a b" and "a_b" do not collapse to the same surface_id.

Examples:
  tools/compute_surface_id.sh verb list                  → verb__list
  tools/compute_surface_id.sh flag list --json           → flag__list__json
  tools/compute_surface_id.sh env "" MYTOOL_HOME         → env__MYTOOL_HOME
  tools/compute_surface_id.sh exit "" 1                  → exit__1
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

KIND="$1"

if ! [[ "$KIND" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "invalid surface kind: $KIND" >&2
  echo "(kind must be file-stem-safe: [A-Za-z0-9][A-Za-z0-9._-]*)" >&2
  exit 2
fi

if [ "$#" -lt 3 ]; then
  # 2-arg form: kind + name (no subtree)
  if [ -z "${2:-}" ]; then
    usage >&2
    exit 1
  fi
  NAME="$2"
  SUBTREE=""
else
  SUBTREE="${2:-}"
  NAME="$3"
fi

surface_segment() {
  local raw="$1"
  local clean
  clean=$(printf '%s' "$raw" \
    | LC_ALL=C tr -c 'A-Za-z0-9._-' '_' \
    | sed -E 's/^[^A-Za-z0-9]+//; s/_+/_/g; s/_$//')
  if [ -z "$clean" ]; then
    clean="x$(printf '%s' "$raw" | sha256sum | cut -c1-8)"
  elif [ "$clean" != "$raw" ]; then
    clean="${clean}_h$(printf '%s' "$raw" | sha256sum | cut -c1-8)"
  fi
  printf '%s' "$clean"
}

# Match scripts/inventory_surfaces.sh: flag IDs are computed from the visible
# flag after leading dashes are removed; all other segments use the raw text.
NAME_FOR_ID="$NAME"
if [ "$KIND" = "flag" ]; then
  NAME_FOR_ID=$(printf '%s' "$NAME" | sed -E 's/^-+//')
fi

NAME_NORM=$(surface_segment "$NAME_FOR_ID")

if [ -z "$SUBTREE" ]; then
  printf "%s__%s\n" "$KIND" "$NAME_NORM"
else
  SUBTREE_NORM=$(surface_segment "$SUBTREE")
  printf "%s__%s__%s\n" "$KIND" "$SUBTREE_NORM" "$NAME_NORM"
fi

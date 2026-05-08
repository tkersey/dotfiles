#!/usr/bin/env bash
# scripts/build-canonical-tasks.sh — Build canonical_tasks.md for a target by combining
# universal U-Tasks + archetype-default tasks + README-mined tasks.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/build-canonical-tasks.sh <sibling> <archetype>

Builds <sibling>/audit/canonical_tasks.md for the Phase 9 simulator from
references/exemplars/CANONICAL-TASK-LIBRARY.md. The output combines the
universal U-Tasks with archetype-specific tasks for <archetype>.

Args:
  <sibling>     Audit workspace root.
  <archetype>   One of: search-tool | package-manager | build-tool |
                test-runner | scm | daemon | converter | scaffolder | hook |
                issue-tracker | auth | migration | diagnostic | mcp |
                multi-binary | composite | novel.

Output:
  Writes <sibling>/audit/canonical_tasks.md. Summary on stdout.

Exit codes:
  0  Success.
  1  Missing arguments (usage printed).
  2  CANONICAL-TASK-LIBRARY.md not found.

Example:
  scripts/build-canonical-tasks.sh /path/to/__audit issue-tracker
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

if [ -z "${2:-}" ]; then
  usage >&2
  exit 1
fi

SIBLING="$1"
ARCHETYPE="$2"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIBRARY="$SKILL_DIR/references/exemplars/CANONICAL-TASK-LIBRARY.md"

if [ ! -f "$LIBRARY" ]; then
  echo "missing CANONICAL-TASK-LIBRARY.md" >&2
  exit 2
fi

mkdir -p "$SIBLING/audit"
OUT="$SIBLING/audit/canonical_tasks.md"

# Header
cat > "$OUT" <<EOF
# Canonical Tasks for Phase 9 Simulator

Built: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Archetype: $ARCHETYPE
Source: CANONICAL-TASK-LIBRARY.md

---

EOF

# Section 1: Universal tasks (always).
# Extract content BETWEEN delimiter lines (exclusive); avoids leaking trailing section header.
{
  echo "## Universal tasks (apply regardless of archetype)"
  echo
} >> "$OUT"
awk '
  /^## Universal tasks/         { in_section = 1; next }
  /^## How to use this library/ { in_section = 0 }
  in_section
' "$LIBRARY" >> "$OUT" || true

{
  echo
  echo "---"
  echo
} >> "$OUT"

# Section 2: Archetype-specific tasks
{
  echo "## Archetype-specific tasks ($ARCHETYPE)"
  echo
} >> "$OUT"

# Map archetype names to library section headers
case "$ARCHETYPE" in
  search-tool|search)            section="Search tool tasks" ;;
  package-manager|package_manager|pkg) section="Package manager tasks" ;;
  build-tool|build_tool|build)   section="Build tool tasks" ;;
  test-runner|test_runner|test)  section="Test runner tasks" ;;
  scm|scm-tool|git|git-flavored) section="SCM / git-flavored tool tasks" ;;
  daemon|daemon-cli|server)      section="Daemon / server CLI tasks" ;;
  converter|file-converter)      section="File-format converter tasks" ;;
  scaffolder|generator)          section="Scaffolder / generator tasks" ;;
  hook|hook-tool)                section="Hook tool tasks" ;;
  issue-tracker|task-graph)      section="Issue tracker / task graph tasks" ;;
  auth|credential)               section="Authentication / credential tool tasks" ;;
  migration|migration-tool)      section="Migration tool tasks" ;;
  diagnostic|observability)      section="Diagnostic / observability CLI tasks" ;;
  mcp|mcp-server|mcp-cli)        section="MCP server with companion CLI tasks" ;;
  multi-binary|toolkit|family)   section="Multi-binary toolkit tasks" ;;
  composite)
    echo "(composite archetype: see archetype-specific tasks below for each component)" >> "$OUT"
    section=""
    ;;
  novel|*)
    echo "(novel/unrecognized archetype '$ARCHETYPE': falling back to universal tasks only)" >> "$OUT"
    section=""
    ;;
esac

if [ -n "$section" ]; then
  awk -v section="## $section" '
    $0 == section { in_section = 1; next }
    in_section && /^## / && $0 != section { in_section = 0 }
    in_section { print }
  ' "$LIBRARY" >> "$OUT"
fi

{
  echo
  echo "---"
  echo
  echo "## Tool-specific tasks (mined from README + CASS)"
  echo
  echo "(populate by canonical-task-author subagent based on README examples + CASS findings)"
  echo
} >> "$OUT"

# Print summary
universal_count=$(awk '/## Universal tasks/{flag=1; next} /## How to use/{flag=0} flag && /^### U-Task/' "$LIBRARY" | wc -l)
archetype_count=$(if [ -n "$section" ]; then
  awk -v section="## $section" '
    $0 == section { in_section = 1; next }
    in_section && /^## / && $0 != section { in_section = 0 }
    in_section && /^### Task/
  ' "$LIBRARY" | wc -l
else
  echo 0
fi)

echo "canonical_tasks.md built at $OUT"
echo "  universal tasks: $universal_count"
echo "  archetype tasks ($ARCHETYPE): $archetype_count"
echo "  tool-specific tasks: 0 (canonical-task-author can fill in)"

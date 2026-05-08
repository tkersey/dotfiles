#!/usr/bin/env bash
# scripts/scaffold-workspace.sh — Create the audit workspace at <SIBLING> and git-init it.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/scaffold-workspace.sh <sibling> <target>

Creates the sibling audit workspace: directory tree (audit/, audit/partial/,
audit/regression_tests/, audit/agent_simulations/{pre,post}_pass_1/,
audit/triangulation/, tools/), .gitignore, README.md, and `git init`s the
sibling. Idempotent — if audit/manifest.json already exists, exits 0
without overwriting.

Args:
  <sibling>   Absolute path where the workspace should be created. Convention
              is <target>__agent_ergonomics_audit/ as a sibling of <target>.
  <target>    Absolute path to the target CLI repo (used for the README and
              the recommended_mode hint).

Side effects:
  Creates directories, writes a .gitignore + README.md, runs `git init` and a
  single initial commit in <sibling>. Does not modify <target> in any way.

Exit codes:
  0  Success (or already-scaffolded; resume mode).
  1  Missing or invalid arguments (this usage message printed).

Example:
  scripts/scaffold-workspace.sh /path/to/mytool__agent_ergonomics_audit \
                                /path/to/mytool
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
TARGET="$2"

# Validate <target> exists as a directory BEFORE scaffolding. Without this
# check, a typo'd path like `mytool` (instead of `/path/to/mytool`) is
# silently recorded as `tool_repo: "mytool"` in the manifest — every
# downstream script then fails with confusing "No such file" errors when
# they try to resolve target_sha / tool_repo, with no signal at scaffold
# time about what went wrong.
if [ ! -d "$TARGET" ]; then
  echo "target not a directory: $TARGET" >&2
  echo "(pass an absolute path to the CLI repo; run with --help for usage)" >&2
  exit 1
fi

if [ -d "$SIBLING/audit" ] && [ -f "$SIBLING/audit/manifest.json" ]; then
  echo "audit workspace already exists at $SIBLING; resuming, not overwriting" >&2
  echo "(if you want a fresh start, archive the existing audit/ first)" >&2
  exit 0
fi

mkdir -p "$SIBLING/audit/partial"
mkdir -p "$SIBLING/audit/regression_tests"
mkdir -p "$SIBLING/audit/agent_simulations/pre_pass_1"
mkdir -p "$SIBLING/audit/agent_simulations/post_pass_1"
mkdir -p "$SIBLING/audit/triangulation"
mkdir -p "$SIBLING/audit/.archive"
mkdir -p "$SIBLING/tools"

# Track empty dirs in git (so the layout survives clones with no artifacts yet)
for d in "$SIBLING/audit/regression_tests" \
         "$SIBLING/audit/agent_simulations/pre_pass_1" \
         "$SIBLING/audit/agent_simulations/post_pass_1" \
         "$SIBLING/audit/triangulation" \
         "$SIBLING/tools"; do
  [ ! -e "$d/.gitkeep" ] && touch "$d/.gitkeep"
done

# .gitignore
cat > "$SIBLING/.gitignore" <<'EOF'
# Pass-local scratch
audit/partial/
audit/.archive/

# Don't ignore other audit/ contents — they're the durable artifacts
!audit/
!audit/regression_tests/
!audit/agent_simulations/

# Editor / OS noise
.DS_Store
*.swp
*.tmp
EOF

# README
cat > "$SIBLING/README.md" <<EOF
# Agent Ergonomics Audit Workspace

For tool: \`$(basename "$TARGET")\`
Target: \`$TARGET\`

This is a measurement workspace produced by the
\`agent-ergonomics-and-intuitiveness-maximization-for-cli-tools\` skill.

## Layout

- \`audit/manifest.json\` — entry point (pass number, target SHA, artifact paths)
- \`audit/surface_inventory.jsonl\` — every agent surface discovered
- \`audit/agent_surfaces.jsonl\` — surfaces scored across 11 dimensions
- \`audit/intent_inference_corpus.jsonl\` — wrong-invocation corpus + outcomes
- \`audit/recommendations.jsonl\` — ranked recommendations
- \`audit/applied_changes.jsonl\` — what was applied + commit refs
- \`audit/scorecard.md\` — human-readable scorecard
- \`audit/heatmap.svg\` — surfaces × dimensions heatmap
- \`audit/playbook.md\` — top-10 narrative
- \`audit/uplift_diff.md\` — pass-N vs pass-N-1 deltas
- \`audit/regression_alerts.md\` — surfaces that dropped scores
- \`audit/regression_tests/\` — golden/snapshot tests
- \`audit/agent_simulations/\` — fresh-agent canonical-task transcripts
- \`audit/HANDOFF.md\` — what's queued for next pass

## How to resume

The phase-loop scripts live in the **skill repo**, not in this sibling. From the skill repo's root (or with absolute paths), run:

1. \`<SKILL>/scripts/discover-cli.sh $TARGET\` to confirm the binary still exists.
2. \`<SKILL>/scripts/validate_pass.sh $SIBLING\` to check artifact integrity.
3. Read \`audit/HANDOFF.md\` here in the sibling.
4. Pick a mode and send the resumed-pass kickoff prompt.
EOF

# Initial manifest. Materialize the actual `audit/manifest.json` (not just a
# `.template` copy — every subsequent script reads this file, so the workspace
# is unusable without it). Fill in the concrete tool_name / tool_repo /
# audit_workspace from the args we have, and seed the first pass entry.
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOL_NAME="$(basename "$TARGET")"
TARGET_ABS="$(cd "$TARGET" 2>/dev/null && pwd || echo "$TARGET")"
SIBLING_ABS="$(cd "$SIBLING" && pwd)"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
TARGET_SHA="$(cd "$TARGET" 2>/dev/null && git rev-parse HEAD 2>/dev/null || echo unknown)"

if [ -f "$SKILL_DIR/assets/manifest-template.json" ]; then
  # Keep the template around for reference (idempotent).
  cp "$SKILL_DIR/assets/manifest-template.json" "$SIBLING/audit/manifest.json.template"
  # Build a concrete manifest with the seed pass-1 entry.
  jq --arg tool "$TOOL_NAME" \
     --arg repo "$TARGET_ABS" \
     --arg sib  "$SIBLING_ABS" \
     --arg now  "$NOW" \
     --arg sha  "$TARGET_SHA" \
     '. as $base
       | .tool_name = $tool
       | .tool_repo = $repo
       | .audit_workspace = $sib
       | .current_pass = 1
       | .passes = [{
           pass: 1,
           started_at: $now,
           completed_at: null,
           mode: null,
           target_sha: $sha,
           feature_branch: null,
           summary: $base._schema_doc.passes_entry.summary,
           artifacts: $base._schema_doc.passes_entry.artifacts
         }]
       | del(._schema_doc)' \
     "$SKILL_DIR/assets/manifest-template.json" > "$SIBLING/audit/manifest.json"
fi

# Initialize git AFTER manifest creation so the initial commit captures it.
if ! [ -d "$SIBLING/.git" ]; then
  (cd "$SIBLING" && git init -q && git add . && git commit -q -m "Initial scaffold for $(basename "$TARGET") agent-ergonomics audit")
fi

echo "scaffold complete: $SIBLING"
echo "  manifest: $SIBLING/audit/manifest.json (pass=1, mode=null — Phase 0 will set mode)"
exit 0

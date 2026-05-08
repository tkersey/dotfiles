#!/usr/bin/env bash
# scripts/sw-self-audit.sh — Self-audit a Claude Code skill against the agent-ergonomics methodology.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/sw-self-audit.sh <skill-dir>

Treats <skill-dir> as the target and runs a quick structural triage:
SKILL.md frontmatter, body length, references/, subagents/ (with frontmatter
check), scripts/ (executable + shebang check), and SELF-TEST.md.

Args:
  <skill-dir>   Path to a Claude Code skill root (the directory containing
                SKILL.md).

Output:
  Markdown triage report on stdout.

Exit codes:
  0  Skill is structurally sound (or has only warnings).
  1  Structural violations detected (missing SKILL.md, broken frontmatter,
     non-executable scripts, etc.).
  2  Missing arguments, or <skill-dir> does not exist (input error,
     distinct from "violations found" so callers can tell them apart).

Example:
  scripts/sw-self-audit.sh ~/.claude/skills/my-skill
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

SKILL_DIR="$1"

if [ ! -d "$SKILL_DIR" ]; then
  echo "skill dir not found: $SKILL_DIR" >&2
  exit 2
fi

violations=0
warnings=0

cat <<EOF
# Skill Self-Audit Report

Target: $SKILL_DIR
Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)

---

## Frontmatter
EOF

# Check 1: SKILL.md exists with frontmatter
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "**FAIL** — SKILL.md missing"
  violations=$((violations + 1))
else
  if ! head -1 "$SKILL_DIR/SKILL.md" | grep -qE '^---$'; then
    echo "**FAIL** — SKILL.md doesn't start with frontmatter delimiter"
    violations=$((violations + 1))
  fi

  name=$(grep -E '^name:' "$SKILL_DIR/SKILL.md" | head -1 | sed -E 's/name:\s*//')
  echo "- name: \`$name\`"

  # Extract description block. Pipefail can trip when `head` closes the pipe early.
  set +o pipefail
  desc_lines=$(awk '
    /^description:/  { flag=1 }
    flag             { print; if (/^[a-zA-Z_]+:/ && !/^description:/) { flag=0 } }
  ' "$SKILL_DIR/SKILL.md" 2>/dev/null | head -10 | wc -l)
  set -o pipefail
  echo "- description: $desc_lines lines"
  if [ "$desc_lines" -lt 2 ]; then
    echo "  **WARN** — description is short; consider adding trigger phrases + durable artifact paths"
    warnings=$((warnings + 1))
  fi
fi

cat <<EOF

## Body structure

EOF

# Check 2: SKILL.md has TOC / quickref
if [ -f "$SKILL_DIR/SKILL.md" ]; then
  if grep -qE '<!-- TOC' "$SKILL_DIR/SKILL.md"; then
    echo "- ✓ Has TOC marker"
  else
    echo "- **WARN** — No TOC marker; agents must read whole SKILL.md"
    warnings=$((warnings + 1))
  fi

  body_lines=$(wc -l < "$SKILL_DIR/SKILL.md")
  echo "- SKILL.md is $body_lines lines"
  if [ "$body_lines" -gt 600 ]; then
    echo "  **WARN** — SKILL.md is long ($body_lines > 600); consider a CHEAT-SHEET.md for quick reference"
    warnings=$((warnings + 1))
  fi
fi

cat <<EOF

## References

EOF

# Check 3: references directory
ref_count=0
if [ -d "$SKILL_DIR/references" ]; then
  ref_count=$(find "$SKILL_DIR/references" -name '*.md' | wc -l)
  echo "- ✓ references/ exists with $ref_count files"
else
  echo "- **WARN** — no references/ directory"
  warnings=$((warnings + 1))
fi

cat <<EOF

## Subagents

EOF

# Check 4: subagents
if [ -d "$SKILL_DIR/subagents" ]; then
  sub_count=$(find "$SKILL_DIR/subagents" -name '*.md' | wc -l)
  echo "- ✓ subagents/ exists with $sub_count files"

  # Verify each subagent has frontmatter
  no_fm=0
  for s in "$SKILL_DIR"/subagents/*.md; do
    [ -f "$s" ] || continue
    head -1 "$s" | grep -qE '^---$' || no_fm=$((no_fm + 1))
  done
  if [ "$no_fm" -gt 0 ]; then
    echo "  **WARN** — $no_fm subagent(s) lack frontmatter delimiter"
    warnings=$((warnings + 1))
  fi
fi

cat <<EOF

## Scripts

EOF

# Check 5: scripts executable + shebang.
# `2>/dev/null` is not valid in `for x in <words>; do` — words are globs, not commands.
# Use shopt -s nullglob so empty globs expand to nothing instead of literal patterns.
if [ -d "$SKILL_DIR/scripts" ]; then
  no_exec=0; no_shebang=0
  shopt -s nullglob
  for s in "$SKILL_DIR"/scripts/*.sh "$SKILL_DIR"/scripts/*.mjs "$SKILL_DIR"/scripts/*.py; do
    [ -f "$s" ] || continue
    [ ! -x "$s" ] && no_exec=$((no_exec + 1))
    head -1 "$s" 2>/dev/null | grep -qE '^#!' || no_shebang=$((no_shebang + 1))
  done
  shopt -u nullglob
  if [ "$no_exec" -gt 0 ]; then
    echo "- **FAIL** — $no_exec scripts are not executable"
    violations=$((violations + 1))
  fi
  if [ "$no_shebang" -gt 0 ]; then
    echo "- **WARN** — $no_shebang scripts lack shebang line"
    warnings=$((warnings + 1))
  fi
fi

cat <<EOF

## SELF-TEST

EOF

# Check 6: SELF-TEST.md
if [ -f "$SKILL_DIR/SELF-TEST.md" ]; then
  # `grep -c` always prints the count (0 if no matches) but exits 1 when 0 matches.
  # `|| true` lets us swallow that exit without appending a second "0" (which would
  # break the integer compare below).
  trigger_count=$(grep -cE '^- ' "$SKILL_DIR/SELF-TEST.md" 2>/dev/null || true)
  echo "- ✓ SELF-TEST.md exists; ~$trigger_count trigger phrases / list items"
  if [ "$trigger_count" -lt 5 ]; then
    echo "  **WARN** — few trigger phrases; consider adding more"
    warnings=$((warnings + 1))
  fi
else
  echo "- **WARN** — no SELF-TEST.md"
  warnings=$((warnings + 1))
fi

cat <<EOF

## Summary

EOF

echo "- Violations: $violations"
echo "- Warnings: $warnings"

if [ "$violations" -gt 0 ]; then
  echo "- Status: **FAIL** (structural issues)"
  exit 1
elif [ "$warnings" -gt 5 ]; then
  echo "- Status: **WARN** (multiple ergonomic gaps)"
  exit 0
else
  echo "- Status: **OK** (skill is structurally sound; for full audit, invoke the agent-ergonomics skill on this dir)"
  exit 0
fi

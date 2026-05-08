#!/usr/bin/env bash
# scripts/preflight.sh — Pre-flight checks before scaffolding an audit.
#
# Verifies the environment can support the full pipeline before phase
# scripts start writing artifacts. Fails fast (exit 1) on hard requirements
# missing; emits warnings (rc 0) for optional helpers that have inline
# fallbacks. Per the round-I cross-model review (I3-#11..15), the previous
# bootstrap silently assumed git/jq/flock/Beads/Agent-Mail were available;
# if any was missing, audits would fail mid-Phase-N with a confusing error.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/preflight.sh <target-dir>

Checks the environment + target before the skill scaffolds an audit
workspace. Hard requirements fail with exit 1; optional helpers print a
warning (and the inline-fallback path documented in
references/methodology/SKILL-FALLBACKS.md is used).

Args:
  <target-dir>   Path to the target CLI repo to be audited.

Output:
  Per-check `OK <name>` or `MISSING <name>: <hint>` to stderr.
  Final summary line + exit code.

Exit codes:
  0  All hard requirements met (warnings about optional helpers OK).
  1  Hard requirement missing (fix before scaffolding).
  2  Missing arguments (usage printed).
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

TARGET="$1"
fail=0
warn=0

require() {
  local name="$1" hint="$2"
  shift 2
  if "$@" >/dev/null 2>&1; then
    echo "OK    $name" >&2
  else
    echo "FAIL  $name — $hint" >&2
    fail=$((fail + 1))
  fi
}

optional() {
  local name="$1" hint="$2"
  shift 2
  if "$@" >/dev/null 2>&1; then
    echo "OK    $name (optional)" >&2
  else
    echo "WARN  $name (optional) — $hint" >&2
    warn=$((warn + 1))
  fi
}

# shellcheck disable=SC2317 # Invoked indirectly through require/optional's argv dispatcher.
has_skill_or_jsm() {
  local skill="$1" pattern="$2"
  [ -d "$HOME/.claude/skills/$skill" ] \
    || { command -v jsm >/dev/null 2>&1 && jsm list 2>/dev/null | grep -Eq "$pattern"; }
}

# --- Hard requirements ----------------------------------------------------

require "target is a directory"   "pass an absolute path to the CLI repo" test -d "$TARGET"
require "git installed"           "apt install git / brew install git" command -v git
require "jq installed"            "apt install jq / brew install jq (≥ 1.6)" command -v jq
require "flock installed"         "apt install util-linux (already installed on every Linux distro; missing on bare BSD)" command -v flock
require "node installed"          "needed by scripts/synthesize_recommendations.mjs" command -v node
require "awk installed"           "needed by scripts/inventory_surfaces.sh" command -v awk
require "find installed"          "POSIX standard; should always be present" command -v find
require "sed installed"           "POSIX standard; should always be present" command -v sed
require "timeout installed"       "needed by scripts/inventory_surfaces.sh, run_intent_corpus.sh" command -v timeout

if [ -d "$TARGET" ]; then
  require "target is a git repo" \
    "Phase 5 requires git for branching + commits. Run \`cd $TARGET && git init\` first, or pass --no-apply" \
    git -C "$TARGET" rev-parse --is-inside-work-tree
fi

# --- Helper SKILLs (optional with fallbacks) ------------------------------

optional "/agent-mail skill" \
  "without it, applier subagents skip Agent Mail file reservations (single-applier-only mode); see SKILL-FALLBACKS.md" \
  has_skill_or_jsm agent-mail 'agent-mail'
optional "/br (Beads tracker)" \
  "without it, follow-up beads can't be filed; deferred recommendations live only in HANDOFF.md" \
  command -v br
optional "/bv skill" \
  "without it, no bead-graph triage; minor" \
  command -v bv
optional "/cass skill" \
  "without it, Phase 0 CASS mining is skipped; rubric still works without prior session evidence" \
  command -v cass
optional "/multi-model-triangulation skill" \
  "without it, Phase 4 + 7 fall back to peer-claude (two parallel Claude subagents) — still useful, just one model" \
  has_skill_or_jsm multi-model-triangulation 'multi-model-triangulation'
optional "/ubs skill" \
  "without it, Phase 7 fresh-eyes skips static-bug pre-pass; minor" \
  command -v ubs
optional "shellcheck" \
  "without it, applier can't lint bash patches it writes; only matters for bash-language CLIs" \
  command -v shellcheck

# --- Target-specific checks ----------------------------------------------

if [ -d "$TARGET" ]; then
  # Try to discover the binary name from manifest files (best-effort).
  binary=""
  if [ -f "$TARGET/Cargo.toml" ]; then
    binary=$(awk -F'"' '/^\[\[bin\]\]/{f=1; next} f && /^name/{print $2; exit} /^\[/{f=0}' "$TARGET/Cargo.toml" | head -1)
    [ -z "$binary" ] && binary=$(awk -F'"' '/^\[package\]/{f=1; next} f && /^name/{print $2; exit} /^\[/{f=0}' "$TARGET/Cargo.toml" | head -1)
  elif [ -f "$TARGET/package.json" ]; then
    binary=$(jq -r 'if (.bin | type) == "object" then (.bin | keys | first) elif (.bin | type) == "string" then .name else .name // empty end' "$TARGET/package.json" 2>/dev/null)
  elif [ -f "$TARGET/configure.ac" ]; then
    binary=$(grep -oE 'AC_INIT\(\[[^],]+' "$TARGET/configure.ac" 2>/dev/null | head -1 | sed -E 's/AC_INIT\(\[//')
  fi

	if [ -n "$binary" ]; then
		# Check whether the binary is reachable (built, on PATH, or in target/release).
		binary_path=""
		if command -v "$binary" >/dev/null 2>&1; then
			binary_path="$(command -v "$binary")"
			echo "OK    target binary '$binary' on PATH" >&2
		elif [ -x "$TARGET/target/release/$binary" ]; then
			binary_path="$TARGET/target/release/$binary"
			echo "OK    target binary '$binary' present in target/release/ (Rust)" >&2
		elif [ -x "$TARGET/$binary" ]; then
			binary_path="$TARGET/$binary"
			echo "OK    target binary '$binary' present at top level" >&2
		else
			echo "WARN  target binary '$binary' not found on PATH or in $TARGET; build the binary before Phase 1" >&2
			warn=$((warn + 1))
		fi
		if [ -n "$binary_path" ]; then
			# Phase 1 walks --help; verify the resolved tool actually responds to it.
			if timeout 5 "$binary_path" --help >/dev/null 2>&1 || timeout 5 "$binary_path" -h >/dev/null 2>&1; then
				echo "OK    target binary responds to --help / -h" >&2
			else
				echo "WARN  target binary doesn't respond to --help / -h within 5s; Phase 1 may produce empty inventory" >&2
				warn=$((warn + 1))
			fi
		fi
	else
		echo "WARN  could not auto-detect target binary name; user must specify at intake" >&2
		warn=$((warn + 1))
  fi
fi

# --- Summary -------------------------------------------------------------

echo >&2
if [ "$fail" -gt 0 ]; then
  echo "preflight: $fail hard requirement(s) FAILED, $warn warning(s)" >&2
  exit 1
fi
echo "preflight: OK ($warn optional helper warning(s); see SKILL-FALLBACKS.md)" >&2
exit 0

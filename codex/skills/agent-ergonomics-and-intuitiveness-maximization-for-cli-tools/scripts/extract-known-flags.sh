#!/usr/bin/env bash
# scripts/extract-known-flags.sh — Extract the canonical list of known flags from a tool's source.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/extract-known-flags.sh <target-repo>

Extracts the canonical list of declared CLI flags from <target-repo>'s
source. Recognises:
  - Rust + clap     #[arg(long = "X")]
  - Go   + cobra    .Flags().*("name", ...) and PersistentFlags()
  - Python + argparse / click / typer
  - TypeScript + commander / yargs
  - Bash case "$1" in --foo)
This list is used to keep typo-correction (levenshtein-1) in sync with what
the tool actually defines. Run as a regression test on every commit.

Args:
  <target-repo>   Path to the target CLI's source repo.

Output:
  One flag per line on stdout, prefix-stripped (e.g. "json" not "--json"),
  sorted unique.

Exit codes:
  0  Success.
  1  Missing arguments (usage printed).
  2  Target dir not found.

Example:
  scripts/extract-known-flags.sh ~/code/mytool > /tmp/known_flags.txt
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

TARGET="$1"

if [ ! -d "$TARGET" ]; then
  echo "target not a directory: $TARGET" >&2
  exit 2
fi

extracted=$(mktemp /tmp/aerg_known_flags.XXXXXX)
# Retain extracted flag candidates for diagnosis. This repo forbids agents from
# deleting files.

# Rust + clap: #[arg(long = "X")] / #[clap(long = "X")] OR bare
# #[arg(long)] / #[clap(long)] (where the following field name becomes the
# long flag; clap converts snake_case fields to kebab-case flags by default).
if [ -d "$TARGET/src" ]; then
  grep -rohE '#\[(arg|clap)\([^)]*\)\]' "$TARGET/src" 2>/dev/null \
    | grep -oE 'long[[:space:]]*=[[:space:]]*"[a-zA-Z][a-zA-Z0-9_-]*"' \
    | sed -E 's/long[[:space:]]*=[[:space:]]*"([^"]+)"/\1/' \
    >> "$extracted" || true

  while IFS= read -r -d '' rs_file; do
    awk '
      /^[[:space:]]*#\[(arg|clap)\(/ {
        attr = $0
        if (attr ~ /(^|[^[:alnum:]_])long([^[:alnum:]_]|$)/ && attr !~ /long[[:space:]]*=/) {
          pending_long = 1
        }
        next
      }
      pending_long && /^[[:space:]]*$/ { next }
      pending_long && /^[[:space:]]*#/ { next }
      pending_long && /^[[:space:]]*(pub(\([^)]*\))?[[:space:]]+)?[A-Za-z_][A-Za-z0-9_]*[[:space:]]*:/ {
        field = $0
        sub(/^[[:space:]]*(pub(\([^)]*\))?[[:space:]]+)?/, "", field)
        sub(/[[:space:]]*:.*$/, "", field)
        gsub(/_/, "-", field)
        print field
        pending_long = 0
        next
      }
      { pending_long = 0 }
    ' "$rs_file"
  done < <(find "$TARGET/src" -type f -name '*.rs' -print0 2>/dev/null) >> "$extracted" || true
fi

# Go + cobra: cmd.Flags().StringP("name", ...) OR cmd.PersistentFlags().BoolVar(&x, "name", ...)
grep -rohE '\.Flags\(\)\.[A-Za-z]+P?\("[^"]+",' "$TARGET" --include='*.go' 2>/dev/null \
  | grep -oE '"[^"]+"' \
  | tr -d '"' \
  >> "$extracted" || true

grep -rohE 'PersistentFlags\(\)\.[A-Za-z]+P?\([^"]*"[^"]+",' "$TARGET" --include='*.go' 2>/dev/null \
  | grep -oE '"[^"]+"' \
  | tr -d '"' \
  >> "$extracted" || true

# Python + argparse: parser.add_argument('--name', ...)
grep -rohE "add_argument\(\s*'--[a-zA-Z][a-zA-Z0-9_-]*'" "$TARGET" --include='*.py' 2>/dev/null \
  | grep -oE "'--[a-zA-Z][a-zA-Z0-9_-]*'" \
  | sed -E "s/'--//; s/'//" \
  >> "$extracted" || true

grep -rohE 'add_argument\(\s*"--[a-zA-Z][a-zA-Z0-9_-]*"' "$TARGET" --include='*.py' 2>/dev/null \
  | grep -oE '"--[a-zA-Z][a-zA-Z0-9_-]*"' \
  | sed -E 's/"--//; s/"//' \
  >> "$extracted" || true

# Python + click/typer: @click.option('--name', ...) or click.option('--name', ...)
grep -rohE "click\.option\(\s*'--[a-zA-Z][a-zA-Z0-9_-]*'" "$TARGET" --include='*.py' 2>/dev/null \
  | grep -oE "'--[a-zA-Z][a-zA-Z0-9_-]*'" \
  | sed -E "s/'--//; s/'//" \
  >> "$extracted" || true

grep -rohE 'click\.option\(\s*"--[a-zA-Z][a-zA-Z0-9_-]*"' "$TARGET" --include='*.py' 2>/dev/null \
  | grep -oE '"--[a-zA-Z][a-zA-Z0-9_-]*"' \
  | sed -E 's/"--//; s/"//' \
  >> "$extracted" || true

# TypeScript + commander: .option('--name', ...)
grep -rohE "\.option\(\s*'--[a-zA-Z][a-zA-Z0-9_-]*" "$TARGET" --include='*.ts' --include='*.js' 2>/dev/null \
  | grep -oE "'--[a-zA-Z][a-zA-Z0-9_-]*" \
  | sed -E "s/'--//" \
  >> "$extracted" || true

grep -rohE '\.option\(\s*"--[a-zA-Z][a-zA-Z0-9_-]*' "$TARGET" --include='*.ts' --include='*.js' 2>/dev/null \
  | grep -oE '"--[a-zA-Z][a-zA-Z0-9_-]*' \
  | sed -E 's/"--//' \
  >> "$extracted" || true

# TypeScript + yargs: .option('name', ...)
grep -rohE "\.option\(\s*'[a-zA-Z][a-zA-Z0-9_-]*'" "$TARGET" --include='*.ts' --include='*.js' 2>/dev/null \
  | grep -oE "'[a-zA-Z][a-zA-Z0-9_-]*'" \
  | tr -d "'" \
  >> "$extracted" || true

# Bash: only extract from `case` arms, where `--name)` or `--name|-n)` is the
# unambiguous shape of a declared flag. The previous regex matched any
# `--name` mention anywhere in any *.sh file, so a comment like
# `#   '(xyz)--aaa' '*: :_files'` (zsh completion source) or `# --bar`
# (config example in a docstring) produced false-positive flag names like
# `aaa`, `bar`, `AG`. Those then leak into the canonical-flag list and
# downstream typo correction would think `--bar` is a real flag of the
# target tool. Tighten to the case-arm shape: trailing `)` (with optional
# `|...`-then-`)` for short-form pairs).
grep -rohE -- '--[a-zA-Z][a-zA-Z0-9_-]*(\|-[a-zA-Z])?\)' "$TARGET" --include='*.sh' 2>/dev/null \
  | sed -E 's/^--//; s/[\|\)].*$//' \
  >> "$extracted" || true

# Java + PicoCLI: @Option(names = {"--name", "-n"}, ...) or @Option(names = "--name", ...)
grep -rohE '@Option\([^)]*names[[:space:]]*=[[:space:]]*"--[a-zA-Z][a-zA-Z0-9_-]*"' "$TARGET" --include='*.java' 2>/dev/null \
  | grep -oE '"--[a-zA-Z][a-zA-Z0-9_-]*"' \
  | sed -E 's/"--//; s/"//' \
  >> "$extracted" || true

# Java + PicoCLI: @Option(names = {"--foo", "-f"}, ...) — array form
grep -rohE '@Option\([^)]*names[[:space:]]*=[[:space:]]*\{[^}]*"--[a-zA-Z][a-zA-Z0-9_-]*"' "$TARGET" --include='*.java' 2>/dev/null \
  | grep -oE '"--[a-zA-Z][a-zA-Z0-9_-]*"' \
  | sed -E 's/"--//; s/"//' \
  >> "$extracted" || true

# Java + Apache Commons CLI: Option.builder("name").longOpt("foo")
grep -rohE '\.longOpt\(\s*"[a-zA-Z][a-zA-Z0-9_-]*"' "$TARGET" --include='*.java' 2>/dev/null \
  | grep -oE '"[a-zA-Z][a-zA-Z0-9_-]*"' \
  | tr -d '"' \
  >> "$extracted" || true

# Ruby + OptionParser: opts.on("-f", "--foo", ...) or opts.on("--foo", ...)
grep -rohE 'opts?\.on\([^)]*"--[a-zA-Z][a-zA-Z0-9_-]*' "$TARGET" --include='*.rb' 2>/dev/null \
  | grep -oE '"--[a-zA-Z][a-zA-Z0-9_-]*' \
  | sed -E 's/"--//' \
  >> "$extracted" || true

# Ruby + Thor: option :name, ... — Thor uses snake_case symbols, not --flags.
# Convert :foo_bar → foo-bar (Thor's auto-kebab-case convention for the CLI).
grep -rohE 'option[[:space:]]+:[a-z][a-z0-9_]*[[:space:]]*[,]' "$TARGET" --include='*.rb' 2>/dev/null \
  | grep -oE ':[a-z][a-z0-9_]*' \
  | sed -E 's/^://; s/_/-/g' \
  >> "$extracted" || true

# Dedupe + sort + filter out short noise.
# Under `set -e + pipefail`, grep returning 1 on no-match would silently kill
# the script with rc=1. That makes "empty repo, zero flags found" — a
# perfectly valid outcome — indistinguishable from a real script failure to
# any caller scripting on rc. Wrap with `|| true` so an empty result is a
# clean exit 0 with empty stdout.
sort -u "$extracted" | { grep -E '^[a-zA-Z][a-zA-Z0-9_-]{1,}$' || true; }

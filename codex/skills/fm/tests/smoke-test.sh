#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cat >"$TMP/fake-fm" <<'FAKE'
#!/bin/bash
printf 'argc=%s\n' "$#"
index=0
for arg in "$@"; do
  printf 'arg[%s]=<%s>\n' "$index" "$arg"
  index=$((index + 1))
done
FAKE
chmod +x "$TMP/fake-fm"

export FM_EXECUTABLE="$TMP/fake-fm"
export FM_SKIP_PTY=1
export FM_ALLOW_NON_DARWIN=1

output="$($ROOT/scripts/fmctl.sh respond \
  --model pcc \
  --instructions 'Be exact.' \
  --prompt '--model system; echo unsafe')"

printf '%s\n' "$output" | grep -F 'arg[0]=<respond>' >/dev/null
printf '%s\n' "$output" | grep -F 'arg[2]=<pcc>' >/dev/null
printf '%s\n' "$output" | grep -F 'arg[5]=<Be exact.>' >/dev/null
printf '%s\n' "$output" | grep -F 'arg[6]=<--text=--model system; echo unsafe>' >/dev/null

printf 'smoke test passed\n'

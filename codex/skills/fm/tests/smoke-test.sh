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

# Bash 3.2 with nounset must treat an empty image list as zero arguments.
no_image_output="$($ROOT/scripts/fmctl.sh respond \
  --model pcc \
  --instructions 'Be exact.' \
  --prompt '--model system; echo unsafe')"

printf '%s\n' "$no_image_output" | grep -F 'argc=7' >/dev/null
printf '%s\n' "$no_image_output" | grep -F 'arg[0]=<respond>' >/dev/null
printf '%s\n' "$no_image_output" | grep -F 'arg[2]=<pcc>' >/dev/null
printf '%s\n' "$no_image_output" | grep -F 'arg[5]=<Be exact.>' >/dev/null
printf '%s\n' "$no_image_output" | grep -F 'arg[6]=<--text=--model system; echo unsafe>' >/dev/null
if printf '%s\n' "$no_image_output" | grep -F '=<--image>' >/dev/null; then
  printf 'unexpected image argument in no-image response\n' >&2
  exit 1
fi

image_path="$TMP/image with space.png"
: >"$image_path"
image_output="$($ROOT/scripts/fmctl.sh respond \
  --image "$image_path" \
  --prompt 'describe image')"

printf '%s\n' "$image_output" | grep -F 'argc=7' >/dev/null
printf '%s\n' "$image_output" | grep -F 'arg[4]=<--image>' >/dev/null
printf '%s\n' "$image_output" | grep -F "arg[5]=<$image_path>" >/dev/null
printf '%s\n' "$image_output" | grep -F 'arg[6]=<--text=describe image>' >/dev/null

printf 'smoke test passed\n'

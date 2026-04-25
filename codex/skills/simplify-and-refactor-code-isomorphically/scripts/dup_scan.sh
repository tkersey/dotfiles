#!/usr/bin/env bash
# Run language-appropriate duplication scanners and emit a unified map.
#
# Usage:  ./dup_scan.sh [run-id] [src-dir]
# Output: refactor/artifacts/<run-id>/duplication_map.{md,json}
#
# Runs (whichever are installed):
#   jscpd, similarity-ts, similarity-rs, similarity-py,
#   pylint --enable=duplicate-code, vulture,
#   dupl (Go), simian (C++/Java),
#   scc (long-file detector — proxy for hidden duplication)

set -euo pipefail

RUN_ID="${1:-$(date +%Y-%m-%d)-pass-1}"
SRC="${2:-src}"
ART="refactor/artifacts/${RUN_ID}"
mkdir -p "${ART}/scans"

echo "[dup_scan] run-id: ${RUN_ID}"
echo "[dup_scan] scanning: ${SRC}"

ran=()

# jscpd (token-based, multi-language)
if command -v jscpd >/dev/null 2>&1; then
  echo "[dup_scan] jscpd"
  jscpd --min-tokens 50 --min-lines 5 --reporters json --output "${ART}/scans/jscpd" "${SRC}" >/dev/null 2>&1 || true
  ran+=("jscpd")
fi

# similarity-* family
for tool in similarity-ts similarity-rs similarity-py; do
  if command -v "${tool}" >/dev/null 2>&1; then
    echo "[dup_scan] ${tool}"
    "${tool}" -p 80 "${SRC}" > "${ART}/scans/${tool}.txt" 2>/dev/null || true
    ran+=("${tool}")
  fi
done

# pylint duplicate-code
if command -v pylint >/dev/null 2>&1 && [[ -n "$(find "${SRC}" -name '*.py' | head -1 2>/dev/null)" ]]; then
  echo "[dup_scan] pylint --enable=duplicate-code"
  pylint --disable=all --enable=duplicate-code --output-format=json "${SRC}" > "${ART}/scans/pylint_dup.json" 2>/dev/null || true
  ran+=("pylint")
fi

# vulture (dead code in Python)
if command -v vulture >/dev/null 2>&1 && [[ -n "$(find "${SRC}" -name '*.py' | head -1 2>/dev/null)" ]]; then
  echo "[dup_scan] vulture (dead code)"
  vulture "${SRC}" > "${ART}/scans/vulture.txt" 2>/dev/null || true
  ran+=("vulture")
fi

# dupl (Go)
if command -v dupl >/dev/null 2>&1 && [[ -f go.mod ]]; then
  echo "[dup_scan] dupl"
  dupl -threshold 50 -plumbing ./... > "${ART}/scans/dupl.txt" 2>/dev/null || true
  ran+=("dupl")
fi

# simian (legacy multi-language)
if command -v simian >/dev/null 2>&1; then
  echo "[dup_scan] simian"
  mapfile -t files < <(find "${SRC}" -type f \( -name '*.c' -o -name '*.cc' -o -name '*.cpp' -o -name '*.h' -o -name '*.hpp' -o -name '*.java' \))
  if (( ${#files[@]} > 0 )); then
    simian -threshold=6 -reportDuplicateText "${files[@]}" > "${ART}/scans/simian.txt" 2>/dev/null || true
    ran+=("simian")
  fi
fi

# scc — long file detector (proxy for internal duplication)
if command -v scc >/dev/null 2>&1; then
  echo "[dup_scan] scc (long-file scan)"
  scc --by-file --format json "${SRC}" 2>/dev/null \
    | jq '[.[] | select(.Lines > 200) | {Filename, Lines, Complexity}]' > "${ART}/scans/scc_long_files.json" || true
  ran+=("scc")
fi

#--- write a placeholder duplication_map.md for manual completion
cat > "${ART}/duplication_map.md" <<EOF
# Duplication Map — ${RUN_ID}

Generated: $(date -u +'%Y-%m-%d %H:%M UTC')
Tools run: ${ran[*]:-(none installed)}
Raw outputs: ${ART}/scans/

## How to fill this in

1. Read the scan outputs above.
2. Cluster similar findings into candidates (assign IDs D1, D2, …).
3. For each candidate, fill the table row below.
4. Pass to score_candidates.py.

| ID  | Kind | Locations | LOC each | × | Type | Notes |
|-----|------|-----------|----------|---|------|-------|
|     |      |           |          |   |      |       |
EOF

#--- emit a JSON pointer that score_candidates.py can read
cat > "${ART}/duplication_map.json" <<EOF
{
  "run_id": "${RUN_ID}",
  "generated_at": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "tools_run": [$(printf '"%s",' "${ran[@]:-}" | sed 's/,$//')]
  ,
  "candidates": []
}
EOF

echo "[dup_scan] done. Edit ${ART}/duplication_map.md to populate candidates."
echo "[dup_scan]   tools that ran: ${ran[*]:-(none)}"

#!/usr/bin/env bash
# scripts/render_scorecard_html.sh — Render agent_surfaces.jsonl → HTML scorecard.
#
# Self-contained HTML (no external CSS / JS). Per-surface table is sortable
# (click column headers); each row has a hover-tooltip showing evidence; cells
# colored red→yellow→green by score. Embeds the heatmap-style colormap inline.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/render_scorecard_html.sh <agent_surfaces.jsonl> [--pass N | --all-passes]

Renders an HTML scorecard. Self-contained (inline CSS + minimal JS for sort).
Identical pass-filter semantics as scripts/render_scorecard.sh:
  Default: latest pass in the file
  --pass N: filter to specific pass
  --all-passes: every record (no filter)

Args:
  <agent_surfaces.jsonl>   Phase 2 / Phase 6 scoring output.

Output:
  HTML document on stdout. Redirect to <sibling>/audit/scorecard.html.

Exit codes:
  0  Success.
  1  Missing arguments (usage printed).
  2  Input file not found.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

JSONL="$1"
PASS_FILTER=""
ALL_PASSES=false
need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 1; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 1 ;; esac
}
case "${2:-}" in
  "") ;;
  --pass)
    need_value "$2" "${3:-}"
    if [ -n "${4:-}" ]; then
      echo "unexpected extra argument: $4" >&2
      exit 1
    fi
    PASS_FILTER="$3"
    ;;
  --all-passes)
    if [ -n "${3:-}" ]; then
      echo "unexpected extra argument: $3" >&2
      exit 1
    fi
    ALL_PASSES=true
    ;;
  *) echo "unknown arg: $2" >&2; exit 1 ;;
esac

[ -f "$JSONL" ] || { echo "scorecard input not found: $JSONL" >&2; exit 2; }

TMP=""
# shellcheck disable=SC2317 # invoked by the EXIT trap
cleanup() { [ -n "$TMP" ] && [ -f "$TMP" ] && : > "$TMP"; }
trap cleanup EXIT

html_escape() {
  sed \
    -e 's/&/\&amp;/g' \
    -e 's/</\&lt;/g' \
    -e 's/>/\&gt;/g' \
    -e 's/"/\&quot;/g' \
    -e "s/'/\&#39;/g"
}

SOURCE_PATH="$JSONL"
if [ -z "$PASS_FILTER" ] && [ "$ALL_PASSES" = false ]; then
  PASS_FILTER=$(jq -r '.pass // 1' "$JSONL" | sort -n | tail -1)
fi
if [ -n "$PASS_FILTER" ]; then
  TMP=$(mktemp /tmp/aerg_scorecard_html.XXXXXX)
  jq -c --arg p "$PASS_FILTER" 'select((.pass // 1) == ($p | tonumber))' "$JSONL" > "$TMP"
  JSONL="$TMP"
fi

# Build the per-surface JSON array for client-side sort. Keep it out of the
# literal <script> text so data containing </script> cannot terminate the block.
ROWS_JSON_B64=$(jq -c -s 'map({
  sid: .surface_id,
  weighted: .weighted_score,
  scores: .scores,
  evidence: (.evidence // {}),
  notes: (.notes // ""),
  conf: .score_confidence
})' "$JSONL" | base64 | tr -d '\n')

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
N_ROWS=$(jq -r -s 'length' "$JSONL")
PASS_LABEL="${PASS_FILTER:+pass $PASS_FILTER}"
SOURCE_PATH_HTML=$(printf '%s' "$SOURCE_PATH" | html_escape)
PASS_LABEL_HTML=$(printf '%s' "$PASS_LABEL" | html_escape)

# HTML output. Self-contained; uses one small <script> for column-sort.
cat <<HTML
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Agent Ergonomics Scorecard${PASS_LABEL:+ — $PASS_LABEL_HTML}</title>
<style>
  body { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; margin: 24px; max-width: 1400px; color: #222; }
  h1 { margin: 0 0 4px; font-size: 18px; }
  .meta { color: #666; font-size: 12px; margin-bottom: 16px; }
  table { border-collapse: collapse; width: 100%; font-size: 12px; }
  th { background: #f5f5f5; padding: 6px 8px; text-align: left; cursor: pointer; user-select: none; border-bottom: 2px solid #ccc; }
  th:hover { background: #ebebeb; }
  th.sorted-asc::after  { content: " ▲"; color: #888; }
  th.sorted-desc::after { content: " ▼"; color: #888; }
  td { padding: 4px 8px; border-bottom: 1px solid #eee; vertical-align: top; }
  td.sid { font-weight: 600; color: #333; min-width: 250px; }
  td.score { text-align: center; min-width: 50px; position: relative; }
  td.score.bad   { background: #f4c7c3; }
  td.score.poor  { background: #fce5b5; }
  td.score.ok    { background: #fcf2c0; }
  td.score.good  { background: #d4e9d4; }
  td.score.great { background: #b8dcb8; }
  td.score:hover .ev { display: block; }
  .ev { display: none; position: absolute; top: 100%; left: 0; background: #333; color: white; padding: 6px 8px; border-radius: 4px; z-index: 10; white-space: pre-wrap; max-width: 480px; font-size: 11px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
  .legend { margin-top: 24px; font-size: 11px; color: #666; }
  .legend span { display: inline-block; width: 30px; height: 14px; vertical-align: middle; margin-right: 4px; }
</style>
</head>
<body>
<h1>Agent Ergonomics Scorecard</h1>
<div class="meta">Generated: $NOW · Source: <code>$SOURCE_PATH_HTML</code>${PASS_LABEL:+ · $PASS_LABEL_HTML} · $N_ROWS surfaces</div>

<table id="t">
<thead>
<tr>
  <th data-key="sid">surface_id</th>
  <th data-key="weighted" class="num">weighted</th>
  <th data-key="agent_intuitiveness" class="num">intu</th>
  <th data-key="agent_ergonomics" class="num">ergo</th>
  <th data-key="agent_ease_of_use" class="num">ease</th>
  <th data-key="output_parseability" class="num">parse</th>
  <th data-key="error_pedagogy" class="num">error</th>
  <th data-key="intent_inference" class="num">intent</th>
  <th data-key="safety_with_recovery" class="num">safe</th>
  <th data-key="determinism_and_reproducibility" class="num">det</th>
  <th data-key="self_documentation" class="num">self</th>
  <th data-key="composability" class="num">comp</th>
  <th data-key="regression_resistance" class="num">regr</th>
</tr>
</thead>
<tbody id="tb"></tbody>
</table>

<div class="legend">
  Cell colors: <span style="background:#f4c7c3"></span> &lt; 400 ·
  <span style="background:#fce5b5"></span> 400–599 ·
  <span style="background:#fcf2c0"></span> 600–699 ·
  <span style="background:#d4e9d4"></span> 700–799 ·
  <span style="background:#b8dcb8"></span> ≥ 800 (Polish Bar = 750)
</div>

<script>
const ROWS_BYTES = Uint8Array.from(atob('$ROWS_JSON_B64'), c => c.charCodeAt(0));
const ROWS = JSON.parse(new TextDecoder().decode(ROWS_BYTES));
const DIMS = ['agent_intuitiveness','agent_ergonomics','agent_ease_of_use','output_parseability','error_pedagogy','intent_inference','safety_with_recovery','determinism_and_reproducibility','self_documentation','composability','regression_resistance'];

function bucket(s) {
  if (s == null || s === '') return '';
  if (s < 400) return 'bad';
  if (s < 600) return 'poor';
  if (s < 700) return 'ok';
  if (s < 800) return 'good';
  return 'great';
}

function render(rows) {
  const tb = document.getElementById('tb');
  tb.innerHTML = '';
  for (const r of rows) {
    const tr = document.createElement('tr');
    const sid = document.createElement('td');
    sid.className = 'sid';
    sid.textContent = r.sid;
    tr.appendChild(sid);
    const w = document.createElement('td');
    w.className = 'score ' + bucket(r.weighted);
    w.textContent = r.weighted ?? '-';
    tr.appendChild(w);
    for (const d of DIMS) {
      const td = document.createElement('td');
      const v = (r.scores && r.scores[d] != null) ? r.scores[d] : null;
      td.className = 'score ' + bucket(v);
      td.textContent = v ?? '-';
      const ev = (r.evidence && r.evidence[d]) ? r.evidence[d] : null;
      if (ev) {
        const tip = document.createElement('div');
        tip.className = 'ev';
        tip.textContent = (typeof ev === 'string') ? ev : JSON.stringify(ev, null, 2);
        td.appendChild(tip);
      }
      tr.appendChild(td);
    }
    tb.appendChild(tr);
  }
}

// Initial render: sort by weighted desc.
let sortKey = 'weighted', sortDir = 'desc';
function sortRows() {
  const sorted = [...ROWS].sort((a, b) => {
    const va = sortKey === 'sid' ? a.sid : (sortKey === 'weighted' ? a.weighted : (a.scores && a.scores[sortKey]));
    const vb = sortKey === 'sid' ? b.sid : (sortKey === 'weighted' ? b.weighted : (b.scores && b.scores[sortKey]));
    if (va == null) return 1;
    if (vb == null) return -1;
    if (typeof va === 'string') return sortDir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
    return sortDir === 'asc' ? va - vb : vb - va;
  });
  render(sorted);
  for (const th of document.querySelectorAll('th')) {
    th.classList.remove('sorted-asc', 'sorted-desc');
    if (th.dataset.key === sortKey) th.classList.add('sorted-' + sortDir);
  }
}
for (const th of document.querySelectorAll('th')) {
  th.addEventListener('click', () => {
    if (sortKey === th.dataset.key) sortDir = (sortDir === 'asc' ? 'desc' : 'asc');
    else { sortKey = th.dataset.key; sortDir = 'desc'; }
    sortRows();
  });
}
sortRows();
</script>
</body>
</html>
HTML
exit 0

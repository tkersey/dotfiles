#!/usr/bin/env bash
# ai_slop_detector.sh — scan for vibe-coded pathologies P1-P40.
# See references/VIBE-CODED-PATHOLOGIES.md.
#
# Usage: ai_slop_detector.sh [src-dir] [run-id]
# Writes: refactor/artifacts/<run-id>/slop_scan.md

set -euo pipefail

SRC="${1:-src}"
RUN_ID="${2:-$(date +%Y-%m-%d)-pass-1}"
ART="refactor/artifacts/${RUN_ID}"
mkdir -p "$ART"
OUT="$ART/slop_scan.md"
SRC_Q="$(printf '%q' "$SRC")"

log() { printf '[ai_slop] %s\n' "$*" >&2; }

# The scanner relies on ripgrep's language filters (`--type ts`, `--type rust`,
# etc.). A grep fallback would silently drop most findings, so fail explicitly.
if command -v rg >/dev/null 2>&1; then
  RG="rg"
else
  echo "error: ai_slop_detector.sh requires ripgrep (rg) for language-aware scans" >&2
  exit 2
fi

{
  printf '# AI slop scan — %s\n\n' "$RUN_ID"
  printf 'Generated %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'Scope: `%s`\n\n' "$SRC"
  printf '(See references/VIBE-CODED-PATHOLOGIES.md for P1-P40 catalog.)\n\n'
} > "$OUT"

section() { printf '\n## %s\n\n' "$*" >> "$OUT"; }
capture() {
  local label="$1"; shift
  section "$label"
  if out=$("$@" 2>/dev/null); then
    if [[ -n "$out" ]]; then
      printf '```\n%s\n```\n' "$out" >> "$OUT"
    else
      printf '_none found_\n' >> "$OUT"
    fi
  else
    printf '_none found_\n' >> "$OUT"
  fi
}

log "scanning $SRC"

# P1 — over-defensive try/catch (Python + TS)
capture "P1 over-defensive try/catch (Python: ≥3 except Exception per file)" \
  bash -c "$RG 'except Exception' $SRC_Q 2>/dev/null | awk -F: '{f=\$1; c[f]++} END{for(k in c) if(c[k]>=3) print c[k]\"\t\"k}' | sort -rn | head -30"

capture "P1 over-defensive try/catch (TS: catch blocks per file)" \
  bash -c "$RG 'catch\\s*[({]' $SRC_Q --type ts --type tsx 2>/dev/null | awk -F: '{f=\$1; c[f]++} END{for(k in c) if(c[k]>=3) print c[k]\"\t\"k}' | sort -rn | head -30"

# P2 — nullish chain sprawl
capture "P2 long nullish/optional chains (three+ \`?.\`)" \
  bash -c "$RG -n '\\?\\..*\\?\\..*\\?\\.' $SRC_Q --type ts --type tsx 2>/dev/null | head -40"

capture "P2 double-nullish coalescing" \
  bash -c "$RG -n '\\?\\?.*\\?\\?' $SRC_Q --type ts --type tsx 2>/dev/null | head -40"

# P3 — orphan _v2 / _new / _improved / _copy files
capture "P3 orphaned _v2/_new/_old/_improved/_copy files" \
  bash -c "find $SRC_Q -type f 2>/dev/null | grep -iE '(_v[0-9]+|_new|_old|_improved|_enhanced|_final|_copy)\\.(ts|tsx|rs|py|go|cpp|cc|c|h|hpp)$'"

# P4 — utils/helpers/misc/common dumping ground (long files named like these)
capture "P4 utils/helpers/misc/common files > 500 LOC" \
  bash -c "find $SRC_Q -type f \\( -iname 'utils*' -o -iname 'helpers*' -o -iname 'misc*' -o -iname 'common*' -o -iname 'shared*' \\) -exec wc -l {} \\; 2>/dev/null | awk '\$1>500' | sort -rn"

# P5 — BaseXxxManager / AbstractYyy hierarchies
capture "P5 abstract Base/Abstract class hierarchy" \
  bash -c "$RG -n 'extends (Base|Abstract)\\w+' $SRC_Q --type ts --type tsx 2>/dev/null | head -40"

capture "P5 abstract class in Rust (rare idiom; often AI-generated)" \
  bash -c "$RG -n 'pub trait \\w+Manager|pub trait \\w+Factory' $SRC_Q --type rust 2>/dev/null | head -20"

# P6 — feature flags (manual inspection; highlight likely-dead ones)
capture "P6 feature flags (review each for whether it is still toggling)" \
  bash -c "$RG -o '(FEATURE_|FLAG_|ENABLE_|USE_NEW_|LEGACY_)\\w+' $SRC_Q 2>/dev/null | sed 's/^.*://' | sort -u | head -30"

# P7 — re-export webs
capture "P7 re-export barrel files (\`export * from\`)" \
  bash -c "$RG '^export \\* from' $SRC_Q --type ts --type tsx -c 2>/dev/null | sort -t: -k2 -rn | head -20"

# P8 — pass-through wrappers (structural grep would be better)
capture "P8 pass-through wrappers (function whose sole body returns another call)" \
  bash -c "$RG -n 'function \\w+\\([^)]*\\) \\{ return \\w+\\([^)]*\\); \\}' $SRC_Q --type ts --type tsx 2>/dev/null | head -40"

# P9 — parameter sprawl (≥5 optional params)
capture "P9 functions with ≥5 optional parameters" \
  bash -c "$RG -n 'function \\w+\\([^)]*\\?[^)]*\\?[^)]*\\?[^)]*\\?[^)]*\\?' $SRC_Q --type ts --type tsx 2>/dev/null | head -30"

# P10 — swallowed Promise rejections
capture "P10 swallowed catch (empty or \`return null\`)" \
  bash -c "$RG -Un 'catch\\s*\\{\\s*\\}|catch\\s*\\([^)]*\\)\\s*\\{\\s*\\}|catch\\s*\\{\\s*return null' $SRC_Q --type ts --type tsx 2>/dev/null | head -40"

capture "P10 Python: except ... : pass" \
  bash -c "$RG -Un 'except[^:]*:\\s*\\n\\s*pass' $SRC_Q --type py 2>/dev/null | head -40"

# P11 — comment-driven programming
capture "P11 Step/Phase/TODO comments (per-file counts)" \
  bash -c "$RG '^\\s*(#|//)\\s*(Step|Phase|Section|TODO|FIXME|HACK)' $SRC_Q -c 2>/dev/null | sort -t: -k2 -rn | head -20"

# P12 — dead imports (requires ts tool; otherwise heuristic)
capture "P12 many-import files (top 20)" \
  bash -c "$RG '^import ' $SRC_Q --type ts --type tsx -c 2>/dev/null | sort -t: -k2 -rn | head -20"

# P13 — skip (needs type vs runtime audit)

# P14 — mocks
capture "P14 mocks (jest.mock, vi.mock, sinon.stub, __mocks__)" \
  bash -c "$RG -l '__mocks__|jest\\.mock|vi\\.mock|sinon\\.stub' $SRC_Q --type ts --type tsx 2>/dev/null | head -20"

# P15 — \`any\` count
capture "P15 TS \`any\` usage (per-file counts, top 20)" \
  bash -c "$RG ':\\s*any\\b|<any>|\\bas any\\b|\\bas unknown as\\b' $SRC_Q --type ts --type tsx -c 2>/dev/null | sort -t: -k2 -rn | head -20"

# P16 — repeated *Error enums (Rust)
capture "P16 *Error enums in Rust (often duplicate variants)" \
  bash -c "$RG -n 'pub enum \\w+Error' $SRC_Q --type rust 2>/dev/null | head -40"

# P17 — prop drilling heuristic (same prop in many files)
capture "P17 heavily drilled props (top 10 most-passed via JSX)" \
  bash -c "$RG -o '\\b(user|currentUser|theme|locale)={[^}]*}' $SRC_Q --type tsx 2>/dev/null | sort | uniq -c | sort -rn | head -10"

# P18 — everything hook (hooks with many useState/useEffect)
capture "P18 everything hook (custom hook file with many useState/useEffect)" \
  bash -c "while IFS= read -r -d '' f; do n=\$($RG -o 'useState|useEffect' \"\$f\" 2>/dev/null | wc -l | tr -d '[:space:]'); [[ \${n:-0} -ge 8 ]] && printf '%s %s\n' \"\$n\" \"\$f\"; done < <(find $SRC_Q \\( -name '*.tsx' -o -name '*.ts' \\) -print0 2>/dev/null) | sort -rn | head -20"

# P19 — N+1 queries
capture "P19 N+1 pattern (await inside for loop)" \
  bash -c "$RG -Un 'for\\s*\\([^)]+\\)\\s*\\{[^}]*await' $SRC_Q --type ts --type tsx 2>/dev/null | head -20"

capture "P19 Python N+1 (for ... : await)" \
  bash -c "$RG -Un 'for .*:\\s*\\n\\s*.*await' $SRC_Q --type py 2>/dev/null | head -20"

# P20 — config drift
capture "P20 config files (candidates for unification)" \
  bash -c "find . -maxdepth 3 -type f \\( -name '.env*' -o -name 'config*.json' -o -name 'config*.ts' -o -name 'docker-compose*.yml' \\) 2>/dev/null | head"

# P21 — shallow tests — skip programmatic detection (needs mutation score)

# P22 — stringly-typed state machines
capture "P22 stringly-typed status/state comparisons" \
  bash -c "$RG -n \"\\.(status|state)\\s*(===|==|!=|!==)\\s*['\\\"][^'\\\"]+['\\\"]\" $SRC_Q --type ts --type tsx 2>/dev/null | head -50"

capture "P22 Rust stringly-typed status/state comparisons" \
  bash -c "$RG -n '(status|state).*==\\s*\"[^\"]+\"' $SRC_Q --type rust 2>/dev/null | head -40"

# P23 — reflex normalization that may destroy payload
capture "P23 reflex trim/lower/upper normalization" \
  bash -c "$RG -n '\\.trim\\(\\)|\\.toLowerCase\\(\\)|\\.toUpperCase\\(\\)|\\.strip\\(\\)|\\.lower\\(\\)|\\.upper\\(\\)|\\.to_lowercase\\(\\)' $SRC_Q 2>/dev/null | head -80"

# P24 — testability wrappers without real test seams
capture "P24 testability wrappers / mutable deps seams" \
  bash -c "$RG -n 'for testability|to enable mocking|export const deps\\s*=|let deps\\s*=|var deps\\s*=' $SRC_Q --type ts --type tsx 2>/dev/null | head -50"

# P25 — suspicious auto-generated docs/docstrings
capture "P25 docstrings/comments that may contradict implementation" \
  bash -c "$RG -n 'Returns:|Raises:|Throws:|@returns|@throws|TODO: update docs|Generated by|Auto-generated' $SRC_Q 2>/dev/null | head -80"

# P26 — type assertions that paper over real types
capture "P26 TypeScript type assertions" \
  bash -c "$RG -n '\\bas\\s+[A-Z][A-Za-z0-9_<>]*\\b|as unknown as|as any' $SRC_Q --type ts --type tsx 2>/dev/null | head -80"

# P27 — listener leaks
capture "P27 addEventListener sites (audit for cleanup)" \
  bash -c "$RG -n 'addEventListener\\(' $SRC_Q --type ts --type tsx 2>/dev/null | head -80"

# P28 — timer leaks
capture "P28 timers (audit for clearTimeout/clearInterval cleanup)" \
  bash -c "$RG -n 'setTimeout\\(|setInterval\\(' $SRC_Q --type ts --type tsx 2>/dev/null | head -80"

# P29 — regex compiled per-call / in hot path
capture "P29 regex construction in functions/loops" \
  bash -c "$RG -n 'Regex::new\\(|new RegExp\\(|re\\.(match|search|findall)\\(' $SRC_Q 2>/dev/null | head -80"

# P30 — debug prints in production paths
capture "P30 debug print/log leftovers" \
  bash -c "$RG -n 'console\\.(log|debug|trace)\\(|dbg!\\(|println!\\(|eprintln!\\(|^\\s*print\\(' $SRC_Q 2>/dev/null | head -80"

# P31 — JSON.stringify cache/hash/memo keys
capture "P31 JSON.stringify used as key/hash/memo identity" \
  bash -c "$RG -n 'JSON\\.stringify\\([^)]*(key|cache|hash|memo|id)|(?:key|cacheKey|hash|memoKey)\\s*=\\s*JSON\\.stringify' $SRC_Q --type ts --type tsx 2>/dev/null | head -60"

# P32 — float arithmetic for money
capture "P32 money-like arithmetic (audit integer cents/decimal)" \
  bash -c "$RG -n '(price|amount|total|subtotal|tax|shipping|balance|cents|dollars).*[+*/-].*[0-9]+\\.[0-9]+' $SRC_Q 2>/dev/null | head -60"

# P33 — timezone drift
capture "P33 local time / UTC drift candidates" \
  bash -c "$RG -n 'datetime\\.now\\(|datetime\\.utcnow\\(|new Date\\(\\)|Date\\.now\\(|time\\.Now\\(' $SRC_Q 2>/dev/null | head -80"

# P34 — implementation details leaked in errors
capture "P34 detailed internal errors exposed" \
  bash -c "$RG -n 'throw new Error\\(.*(sql|query|params|stack)|return .*err\\.message|format!\\(.*(sql|query|params)' $SRC_Q 2>/dev/null | head -60"

# P35 — wrong auto-import candidates
capture "P35 suspicious ambiguous imports" \
  bash -c "$RG -n \"from ['\\\"](path|url|querystring|util|events|stream)['\\\"]|use std::(path|str|fmt)::\" $SRC_Q 2>/dev/null | head -80"

# P36 — infra change surfaces (review diff separately)
capture "P36 infra/config surfaces that should not ride with refactor commits" \
  bash -c "find . -maxdepth 3 -type f \\( -path './.github/workflows/*' -o -name 'package.json' -o -name 'pnpm-lock.yaml' -o -name 'Cargo.toml' -o -name 'Cargo.lock' -o -name 'docker-compose*.yml' -o -name 'Dockerfile' \\) 2>/dev/null | head -80"

# P37 — unpinned dependencies (full audit lives in unpinned_deps.sh)
capture "P37 unpinned dependency snippets" \
  bash -c "$RG -n '\"\\*\"|: \"latest\"|git\\+|branch\\s*=|rev\\s*=\\s*\"\"' package.json Cargo.toml pyproject.toml go.mod requirements*.txt 2>/dev/null | head -80"

# P38 — glob imports
capture "P38 wildcard/glob imports" \
  bash -c "$RG -n '^use .*::\\*;|^from .* import \\*|^import \\* as ' $SRC_Q 2>/dev/null | head -80"

# P39 — async added to mostly-sync functions
capture "P39 async functions returning Promise (audit for real await)" \
  bash -c "$RG -n 'async function \\w+\\([^)]*\\)\\s*:?\\s*Promise<|const \\w+\\s*=\\s*async\\s*\\(' $SRC_Q --type ts --type tsx 2>/dev/null | head -80"

# P40 — await/then inside non-async-looking functions
capture "P40 await/then in nearby non-async contexts (manual audit)" \
  bash -c "$RG -n '\\bawait\\b|\\.then\\(' $SRC_Q --type ts --type tsx 2>/dev/null | head -80"

{
  printf '\n---\n'
  printf '\n## Next steps\n\n'
  printf '1. Review each section; confirm which hits are real vs. false positives.\n'
  printf '2. File beads for accepted patterns (one per pathology class).\n'
  printf '3. Proceed to `./scripts/dup_scan.sh` for structural duplication.\n'
  printf '4. Score candidates via `./scripts/score_candidates.py`.\n'
  printf '5. For each accepted candidate: fill isomorphism card, edit, verify, ledger.\n'
  printf '\nFull P1-P40 pathology catalog: `references/VIBE-CODED-PATHOLOGIES.md`.\n'
  printf 'Attack order (cheap wins first): the "AI-slop refactor playbook" in that file.\n'
} >> "$OUT"

log "wrote $OUT"
echo "$OUT"

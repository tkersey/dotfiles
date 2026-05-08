# WORKED-OPERATOR-COMPOSITIONS — Practical examples of operator composition

OPERATORS.md catalogues 33 operators. The composition cheat-sheet shows which operators apply per failing dimension. This file shows **worked examples**: for a real surface with multiple failing dimensions, what does the operator pipeline produce?

These are calibration examples for the recommender (Phase 4). Apply this composition when scoring; expect Phase 5 implementers to follow the chain.

---

## Worked Composition 1: A subcommand verb scoring 400 across 4 dims

### Surface

```jsonc
{
  "surface_id": "verb__sync",
  "kind": "verb",
  "scores": {
    "agent_intuitiveness": 600,
    "agent_ergonomics": 400,        // FAIL
    "agent_ease_of_use": 700,
    "output_parseability": 400,     // FAIL
    "error_pedagogy": 350,          // FAIL
    "intent_inference": 400,        // FAIL
    "safety_with_recovery": 800,
    "determinism_and_reproducibility": 700,
    "self_documentation": 600,
    "composability": 500,
    "regression_resistance": 200
  }
}
```

The verb is the "sync" verb of a hypothetical CLI. It works but is painful for agents.

### Operator pipeline

For `agent_ergonomics`: Σ (Mega-Command), 🔀 (Macros-vs-Granular), ⏱ (Sub-Second-Hot-Path)
For `output_parseability`: 🪧 (Stdout-Data-Stderr-Diag), 🚦 (Exit-Code-Contract), 🔢 (Deterministic-Output), 📦 (Stable-Envelope), 🪟 (Provenance-Field)
For `error_pedagogy`: 🩹 (Error-Teaches), ⟁ (Intent-Infer-Then-Act), 🚫 (Never-Silent-Fail), 🪄 (Recommended-Action)
For `intent_inference`: ⟁ (Intent-Infer-Then-Act), 🩹 (Error-Teaches), 🚫 (Never-Silent-Fail)

Union of operators: **Σ 🔀 ⏱ 🪧 🚦 🔢 📦 🪟 🩹 ⟁ 🚫 🪄**

### Composed recommendation

R-NNN: "Robotify the sync verb (full ergonomic uplift)"

```
Diff sketch:
  1. Add `sync --json` flag emitting universal envelope (Σ, 📦)
  2. Stdout becomes data-only; logs to stderr (🪧)
  3. Exit codes: 0=success, 1=user-input, 4=transient (🚦)
  4. Errors include `did you mean` for typo'd args (⟁, 🩹)
  5. Empty result emits {ok:true, items:[]} not silent_fail (🚫)
  6. JSON includes meta.search_mode, meta.fallback_tier (🪟)
  7. Doctor verb returns recommended_action (🪄)
  8. Sort items before emit (🔢)
  9. Quick-reject filter for sync's hot path (⏱)
  10. Add macro `sync-and-validate` for canonical task (🔀)

Expected uplift:
  agent_ergonomics:    +500 (400 → 900)
  output_parseability: +500 (400 → 900)
  error_pedagogy:      +500 (350 → 850)
  intent_inference:    +400 (400 → 800)
  Total weighted uplift: ~+200 (mean of dim deltas)

Risk: low; all changes are additive. Existing users keep current behavior.

Test plan:
  - audit/regression_tests/R-NNN__sync_envelope.test.sh (Pattern 3)
  - audit/regression_tests/R-NNN__sync_typo_hint.test.sh (Pattern 4)
  - audit/regression_tests/R-NNN__sync_empty_result.test.sh (custom)
  - audit/regression_tests/R-NNN__sync_deterministic.test.sh (Pattern 6)
  - audit/regression_tests/R-NNN__sync_recommended_action.test.sh (Pattern 9)
```

This is the composition output: a single rec with 10 items, lifting 4 dims simultaneously.

---

## Worked Composition 2: An error message that teaches nothing

### Surface

```jsonc
{
  "surface_id": "error__sync__connection_refused",
  "kind": "error",
  "message": "connection refused",
  "scores": {
    "error_pedagogy": 200,         // FAIL
    "intent_inference": 1000,      // n/a
    "self_documentation": 400,     // weak (no link to docs)
    "composability": 1000,         // OK (goes to stderr)
    "...": "all others n/a or 1000"
  }
}
```

### Operator pipeline

For `error_pedagogy`: 🩹 (Error-Teaches), ⟁, 🚫, 🪄
For `self_documentation`: 📜, 📖, 🧭

### Composed recommendation

R-NNN: "Rewrite connection-refused error to be actionable"

Before:
```
error: connection refused
exit 1
```

After:
```
error: failed to connect to <api.example.com:443>: connection refused (after 2 retries)
  is the service up?         mytool doctor --component=remote --json
  retry with longer timeout: mytool sync --timeout=60
  use offline mode:          mytool sync --offline
  configured endpoint:       set via MYTOOL_API or --api flag
  see: mytool capabilities --json | jq '.commands.sync'
exit 4 (transient-failure; retry safe)
```

Operators applied:
- 🩹 (Error-Teaches): names the alternatives
- ⟁ (Intent-Infer-Then-Act): not directly applied; the rec lists the canonical alternatives
- 🚫 (Never-Silent-Fail): exits non-zero; emits useful stderr
- 🪄 (Recommended-Action): structured `recommended_action` not yet in this prose form, but next iteration would add `mytool sync --error-format=json` returning `{recommended_action: {command, rationale}}`
- 📜 (Self-Describing): cites `capabilities --json` for related schema
- 🧭 (Discoverable-From-Help): mentions other surfaces

Expected uplift:
- error_pedagogy: 200 → 950 (+750)
- self_documentation: 400 → 700 (+300)

---

## Worked Composition 3: A flag that doesn't follow conventions

### Surface

```jsonc
{
  "surface_id": "flag__sync__output",
  "kind": "flag",
  "name": "--out",
  "scores": {
    "agent_intuitiveness": 300,    // FAIL ('--out' uncommon; '--output' is canonical)
    "intent_inference": 200,        // FAIL ('--output' typo'd as '--out' isn't corrected)
    "self_documentation": 700,
    "composability": 1000,
    "...": "rest"
  }
}
```

### Operator pipeline

For `agent_intuitiveness`: ① (First-Try-Inevitability), ⟁, 🩹, 🎓
For `intent_inference`: ⟁, 🩹, 🚫

### Composed recommendation

R-NNN: "Rename --out to --output (with deprecation path); add typo correction"

```
Stage 0:
  - Add --output flag (canonical)
  - Add --out as alias (deprecated; emits warning)
  - Both work for ≥ 1 release

Stage 1 (next pass):
  - --out emits deprecation warning AND proceeds
  - --output is documented as canonical

Stage 2 (pass after):
  - --out errors with migration recipe
  - --output remains

Operators applied:
  ① — canonical name --output is first-try-correct
  ⟁ — agent typing --out gets infer-and-act with warning
  🩹 — deprecation message names canonical form

Expected uplift Stage 0:
  agent_intuitiveness: 300 → 800 (+500)  [canonical name now exists]
  intent_inference:    200 → 750 (+550)  [alias proceeds-with-warning]

Risk: medium. Existing scripts using --out keep working but emit warnings.

Test plan:
  - audit/regression_tests/R-NNN__output_canonical.test.sh: --output works
  - audit/regression_tests/R-NNN__out_alias_warns.test.sh: --out works + warns
```

---

## Worked Composition 4: A mutating verb without safety gates

### Surface

```jsonc
{
  "surface_id": "verb__delete",
  "kind": "verb",
  "mutates": true,
  "scores": {
    "safety_with_recovery": 100,      // FAIL — no --yes, no --dry-run
    "error_pedagogy": 400,             // FAIL
    "agent_ergonomics": 600,
    "...": "rest"
  }
}
```

### Operator pipeline

For `safety_with_recovery`: 🛡 (Safe-Alternative-Always), 🩹 (Error-Teaches), 🔬 (Single-Step-Atomicity), 🧷 (Idempotency-Pin)
For `error_pedagogy`: 🩹, 🪄 (Recommended-Action)

### Composed recommendation

R-NNN: "Add safety gates to delete verb"

```
Diff sketch:
  1. Add --dry-run flag showing what would be deleted (🛡)
  2. Add --yes flag (or --force-delete-all) required for actual deletion (🛡)
  3. Without --yes: error with safe alternative names (🩹, 🪄)
  4. Re-running delete X-001 after success: detect "already deleted" (🧷, 🔬)
  5. Optional: --plan flag for richer preview

Error message before:
  error: refusing to delete

Error message after:
  error: 'delete' is destructive; refusing without confirmation
    preview:           mytool delete X-001 --dry-run
    perform:           mytool delete X-001 --yes
    safer alternative: mytool archive X-001  (reversible)
    see: mytool delete --help

  exit 2 (safety-block)

Expected uplift:
  safety_with_recovery: 100 → 950 (+850)
  error_pedagogy:       400 → 850 (+450)

Risk: medium; existing scripts that called `<tool> delete X` now error. Migration: add `--yes` to scripts.

Test plan:
  - Pattern 8 (dangerous-op gate): R-NNN__delete_requires_yes.test.sh
  - Custom: R-NNN__delete_idempotent.test.sh
```

---

## Worked Composition 5: An empty-result surface that silent_fails

### Surface

```jsonc
{
  "surface_id": "verb__search__empty_result",
  "kind": "verb",
  "behavior": "exits 0 with empty stdout when no matches",
  "scores": {
    "error_pedagogy": 100,           // FAIL — empty != distinct from "didn't run"
    "composability": 400,            // FAIL — agent can't tell ran-but-no-match from didn't-run
    "output_parseability": 500       // FAIL — empty stdout isn't parseable JSON
  }
}
```

### Operator pipeline

For `error_pedagogy`: 🚫 (Never-Silent-Fail), 🪄 (Recommended-Action)
For `output_parseability`: 📦 (Stable-Envelope), 🪧 (Stdout-Data-Stderr-Diag)
For `composability`: 🚫, 🪧

### Composed recommendation

R-NNN: "Empty result returns explicit envelope, not silent_fail"

```
Before:
  $ mytool search "no matches"
  $ echo $?
  0
  (empty stdout)

After (--json):
  $ mytool search "no matches" --json
  {"ok":true,"data":{"hits":[],"total":0,"query":"no matches"},"meta":{"data_hash":"..."},"hint":"no matches; try broader query"}
  $ echo $?
  0

After (text):
  $ mytool search "no matches"
  no matches for 'no matches' (search took 23ms)
  hint: try broader query, or 'mytool search --recent' for last 7 days
  $ echo $?
  0

Operators applied:
  🚫 — empty result is now distinguishable from "didn't run"
  📦 — universal envelope with ok:true, data:{hits:[]}
  🪧 — JSON on stdout (machine), prose on stderr (human)
  🪄 — hint suggests next action

Expected uplift:
  error_pedagogy:      100 → 800 (+700)
  composability:       400 → 850 (+450)
  output_parseability: 500 → 900 (+400)
```

---

## Worked Composition 6: A doctor verb that lacks recommended_action

### Surface

```jsonc
{
  "surface_id": "verb__doctor",
  "kind": "verb",
  "scores": {
    "self_documentation": 600,
    "error_pedagogy": 500,            // FAIL
    "output_parseability": 700
  }
}
```

### Operator pipeline

For `error_pedagogy`: 🪄 (Recommended-Action)
For `self_documentation`: 🩻 (Doctor-Mode), 📜, 📖

### Composed recommendation

R-NNN: "Doctor verb returns recommended_action structured field"

```
Before (JSON output):
{
  "components": {
    "search_index": {"state": "degraded"},
    "remote": {"state": "ok"}
  }
}

After (with recommended_action per Operator 🪄):
{
  "ok": true,
  "data": {
    "components": {
      "search_index": {"state": "degraded", "details": "lexical-only fallback active"},
      "remote": {"state": "ok"}
    },
    "operation_outcome": {
      "kind": "health-failure",
      "exit_code_kind": "health-failure"
    },
    "recommended_action": {
      "command": "mytool reindex --semantic --yes",
      "rationale": "search_index has been degraded for >5 min; rebuild semantic index",
      "is_destructive": false,
      "alternatives": [
        {"command": "mytool reindex --dry-run", "purpose": "preview"}
      ]
    },
    "fallbacks_active": [
      {"component": "search", "active_mode": "lexical", "preferred_mode": "hybrid"}
    ]
  },
  "meta": {...}
}

Expected uplift:
  self_documentation: 600 → 950 (+350)
  error_pedagogy:     500 → 900 (+400)
```

---

## How to compose operators yourself

1. **Identify failing dims.** Score < 700 = failing.
2. **Look up operators per dim.** Use OPERATORS.md § Composition cheat-sheet.
3. **Take the union of operators across all failing dims.**
4. **Order them by impact.** Operators that lift multiple dims at once go first.
5. **Write a single composed recommendation.** All operators in one rec means one diff, one test, one apply.
6. **Estimate uplift conservatively.** If 3 dims fail and one fix lifts all 3, don't claim 3x the per-dim uplift; the dims interact.
7. **Cite each operator in the rec's `operators_applied` field.**

---

## When operators contradict

Rare but possible:

- Operator A wants the verb to be terse; Operator B wants it to be verbose
- Operator A wants color in TTY; Operator B wants no color ever

Resolve by Polish-Bar guidance, then by canonical exemplar. If still ambiguous, escalate to user.

Document the resolution in the rec's notes; future passes inherit the choice.

---

## When the failing dims point to root cause vs symptom

Some failing dims are SYMPTOMS of a deeper issue:

- `output_parseability` low because `error_pedagogy` is also low → fixing error_pedagogy may auto-lift parseability
- `agent_intuitiveness` low because `self_documentation` is low → fix the docs first

Group symptoms; fix the root cause. Operators help by making the structural pattern visible.

---

## Cross-rec composition

Sometimes one rec affects multiple surfaces. Sometimes multiple recs affect one surface.

The synthesizer (Phase 4) handles both:
- Merge recs that touch the same surface
- Resolve order (which goes first; which is blocked by which)

The result is a DAG of recs; Phase 5 applies in topological order.

---

## Composition as a spec

Each composed recommendation is a specification:

- WHAT changes (diff sketch)
- WHY (operators applied + dim uplift)
- WHEN (priority + sequencing)
- VERIFY (regression test plan)

A clean spec lets a Phase 5 implementer apply without re-deriving. The recommendation file (`recommendations.jsonl`) preserves these specs.

---

## Related

- `OPERATORS.md` § Composition cheat-sheet — the lookup table
- `methodology/AGENT-PROMPTS.md` § recommender — how the recommender drafts these
- `methodology/PHASES.md` § Phase 4 — synthesis

# Artifacts — templates the skill produces

> Every phase emits a concrete file under `refactor/artifacts/<run-id>/`. No artifact → phase isn't done. These are also the hand-off to reviewers.

## Contents

1. [Layout](#layout)
2. [baseline.md](#baselinemd)
3. [duplication_map.md](#duplication_mapmd)
4. [scored_candidates.md](#scored_candidatesmd)
5. [cards/](#cards)
6. [LEDGER.md](#ledgermd)
7. [REJECTIONS.md](#rejectionsmd)
8. [Run-id convention](#run-id-convention)

---

## Layout

```
refactor/
└── artifacts/
    └── 2026-04-23-shrink-pass-1/
        ├── baseline.md
        ├── tests_before.txt
        ├── loc_before.json
        ├── scc_before.json
        ├── clippy_before.txt          # or tsc_before / mypy_before / vet_before
        ├── duplication_map.md
        ├── duplication_map.json
        ├── scored_candidates.md
        ├── cards/
        │   ├── D1.md
        │   ├── D2.md
        │   └── ...
        ├── goldens/
        │   ├── inputs/
        │   ├── outputs/
        │   └── checksums.txt
        ├── LEDGER.md
        ├── REJECTIONS.md
        ├── tests_after.txt
        ├── loc_after.json
        └── verify_report.md
```

---

## baseline.md

```markdown
# Baseline — <run-id>

Captured: 2026-04-23 14:02 UTC
Branch:   main @ a1b2c3d
Project:  <project name>

## Test suite
- Command: `cargo test --no-fail-fast`
- Pass / Fail / Skip: 342 / 0 / 5
- Duration: 47s
- Output: `tests_before.txt`

## LOC
- Tool: `tokei --output json .`
- Output: `loc_before.json`
- Total: 28_413 (Rust 22_011, JSON 4_002, MD 2_400)

## Complexity
- Tool: `scc --by-file --format json .`
- Mean cyclomatic: 4.2
- Max cyclomatic file: src/parser/mod.rs (32)

## Lint / typecheck
- Command: `cargo clippy --all-targets -- -D warnings`
- Warnings: 0 (treated as errors)
- Output: `clippy_before.txt`

## Goldens
- Inputs:    `goldens/inputs/`  (12 files, totalling 1.3 MB)
- Outputs:   `goldens/outputs/` (24 files: stdout + stderr per input)
- Checksums: `goldens/checksums.txt` (sha256 each)

## Bundle (frontend only)
- Command: `pnpm next build`
- Total gzipped JS: 142 KB
```

---

## duplication_map.md

```markdown
# Duplication Map — <run-id>

Generated: 2026-04-23 14:08 UTC
Tools: similarity-rs (-p 80), jscpd (--min-tokens 50), ast-grep
Total candidates: 14

| ID  | Kind          | Locations                                                    | LOC each | × | Type | Notes                                       |
|-----|---------------|--------------------------------------------------------------|----------|---|------|---------------------------------------------|
| D1  | function      | crates/mail/src/messaging.rs:42, :88, :134                   | 40       | 3 | II   | only `kind` literal differs                  |
| D2  | component     | web/src/btn/{Primary,Secondary,Danger}.tsx                   | 60       | 3 | II   | merge with `variant` prop                    |
| D3  | impl block    | crates/proto/src/{user,post,comment}.rs::impl PartialEq      | 8        | 3 | I    | replace with `#[derive(PartialEq)]`          |
| D4  | parser        | crates/csv/src/lib.rs / crates/tsv/src/lib.rs                | 95       | 2 | III  | only separator differs; bounded             |
| D5  | hook          | web/src/{ProductPage,UserPage,OrderPage,ReportPage}.tsx      | 12       | 4 | II   | extract `useResource(url)`                   |
| D6  | error variant | 4 modules each have `pub enum FooError { ... DbRead, IoErr }`| 6        | 4 | III  | unify via thiserror?                         |
| ... | ...           | ...                                                          | ...      | ...| ... | ...                                          |

(see duplication_map.json for raw scanner output)
```

---

## scored_candidates.md

```markdown
# Scored Candidates — <run-id>

| ID | Predicted ΔLOC | LOC pts | Conf | Risk | Score | Rung | Decision |
|----|----------------|---------|------|------|-------|------|----------|
| D1 | -75            | 4       | 5    | 2    | 10.0  | 3 (enum) | ACCEPT |
| D2 | -120           | 4       | 4    | 1    | 16.0  | 3 (variant prop) | ACCEPT |
| D3 | -16            | 2       | 5    | 1    | 10.0  | 1 (derive) | ACCEPT |
| D4 | -85            | 4       | 3    | 3    | 4.0   | 2 (parameterize) | ACCEPT |
| D5 | -30            | 3       | 4    | 2    | 6.0   | 1 (custom hook) | ACCEPT |
| D6 | -8             | 2       | 2    | 4    | 1.0   | n/a | REJECT (Score < 2.0; risk = error-semantics divergence) |
| ... |                |         |      |      |       |      |        |

Acceptance threshold: 2.0
Total accepted: 5; total predicted ΔLOC: -326 (~1.1% of project)
Order of execution: D3 → D5 → D2 → D1 → D4 (mechanical → structural; lowest-risk first)
```

---

## cards/

One file per accepted candidate. Filled BEFORE editing.

```markdown
# Card D1 — Collapse 3× send_* into send(kind, …)

## Equivalence contract
- Inputs covered:      callers in crates/mail/src/handler.rs (5 sites), tests in tests/integration/send_*.rs
- Ordering preserved:  yes — `archive` then `notify_subscribers` order unchanged
- Tie-breaking:        N/A
- Error semantics:     same — `build_envelope` Err propagates identically; no new From impls
- Laziness:            unchanged — payload borrowed, not collected
- Short-circuit eval:  N/A
- Floating-point:      N/A
- RNG/hash order:      N/A
- Side-effects:        notify_subscribers receives "text" | "image" | "file" exactly as before
- Side-effect order:   archive precedes notify (preserved)
- Type narrowing:      enum Payload<'a> exhaustively matched in `mime()` and `tag()`
- Public API:          `send_text/image/file` retained as thin wrappers (no caller break)

## Verification
- [ ] sha256sum -c goldens/checksums.txt
- [ ] cargo test (must remain 342/0/5)
- [ ] tokei messaging.rs: predicted 221 → 142 (-79)
- [ ] cargo clippy: 0 new warnings
```

---

## LEDGER.md

Appended after each accepted candidate verifies green.

```markdown
# Ledger — <run-id>

| Order | ID | Commit  | File(s)                            | LOC before | LOC after | Δ    | Tests       | Goldens | Lints |
|-------|----|---------|-----------------------------------|------------|-----------|------|-------------|---------|-------|
| 1     | D3 | abc1234 | proto/src/{user,post,comment}.rs  | 312        | 296       | -16  | 342/0/5     | ✓       | 0Δ    |
| 2     | D5 | def5678 | web/src/{Product,User,Order,Report}Page.tsx + useResource | 1140 | 1090 | -50 | 401/0/2 | ✓ | 0Δ |
| 3     | D2 | 9012345 | web/src/btn/*.tsx                  | 192        | 71        | -121 | 401/0/2     | ✓       | 0Δ    |
| 4     | D1 | 6789abc | mail/src/messaging.rs              | 221        | 142       | -79  | 342/0/5     | ✓       | 0Δ    |
| 5     | D4 | def0123 | csv/src/lib.rs + tsv/src/lib.rs    | 195        | 110       | -85  | 342/0/5     | ✓       | 0Δ    |
|       |    |         | TOTAL                              | 2060       | 1709      | -351 |             |         |       |

Predicted total: -326. Actual: -351. Variance: +7.7% (over-delivered, within envelope).
Time spent: ~3.5h (incl. baseline capture and verifies).
```

---

## REJECTIONS.md

```markdown
# Rejections — <run-id>

| ID  | Why rejected                              | Action taken |
|-----|-------------------------------------------|--------------|
| D6  | Score 1.0 — error-semantic divergence high; the four `FooError` enums look similar but each has callers that match on `_` differently | Added comment in each error file explaining the rejection so future scans don't re-propose. |
| D7  | Type IV semantic clone — two `uniq()` impls behave identically only on insertion-orderless inputs; one preserves insertion order | Wrote property test `roundtrip_uniq_preserves_first_seen` to pin behavior; left both. |
| D11 | Type V accidental rhyme — `bytes_to_kib` rhymed with `ms_to_seconds`; merging would couple unit-conversion lifetimes | Added rejection comment to bytes_to_kib. |
```

---

## Run-id convention

Format: `YYYY-MM-DD-<scope>-pass-<N>`

Examples:
- `2026-04-23-shrink-pass-1` — first overall pass on the repo
- `2026-04-23-mail-crate-pass-1` — first scoped pass on one crate
- `2026-04-30-shrink-pass-2` — second pass after pass-1 has shipped and surface has shifted

Run-id appears in:
- The artifact directory name
- Every commit message (`refactor(<scope>): <change> [run 2026-04-23-pass-1]`)
- The rejection log (so future scans know what's been considered)

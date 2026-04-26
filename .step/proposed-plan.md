Iteration: 7

# Add Self-Auditing Token Usage Proof To `$seq`

## Round Delta
- Converted the `$grill-me` contract into an additive `seq token-usage --audit` implementation campaign.
- Locked exact output behavior: stable audit fields, report-only anomalies, appended audit row for grouped output, summary-row enrichment for `--summary`.
- Added deterministic fixtures, real-corpus proof, release/tap proof, and rollback criteria.

## Summary
Goal: make suspiciously large `seq token-usage` totals self-proving for the local Codex session corpus. Chosen path: add an explicit `--audit` flag to `token-usage` that preserves existing output by default, then emits scan counters, raw duplicate diagnostics, monotonic-vs-naive reconciliation, and clearer day-denominator fields only when requested. First wave: implement the audit collector and output contract in `skills-zig`; done means released `seq` via Homebrew reproduces the audit fields on both deterministic fixtures and `~/.codex/sessions`.

## Implementation Brief
1. step=wire CLI flag; owner=implementer; success_criteria=`seq token-usage --help` documents `--audit` and unsupported commands reject it.
2. step=add audit collector; owner=implementer; success_criteria=raw bounded token-count events produce duplicate/reset/null/missing-total counters before dedupe.
3. step=integrate output rows; owner=implementer; success_criteria=summary audit enriches one row and grouped audit appends one `row_kind=audit` row after bucket trimming.
4. step=add deterministic tests; owner=implementer; success_criteria=fixtures prove duplicate-last overcount, reset handling, all output modes, and non-audit compatibility.
5. step=update `$seq` docs; owner=implementer; success_criteria=skill shows `--audit` examples and states local-corpus-not-billing scope.
6. step=validate locally; owner=implementer; success_criteria=`zig build test`, relevant golden tests, `zig build bench -Doptimize=ReleaseFast -- --config perf/frozen/workload_config.json`, and real `~/.codex/sessions` audit run pass.
7. step=release; owner=implementer; success_criteria=next `seq` patch tag, successful release workflow, Homebrew formula update, strict audit, upgrade/test, installed `seq --version`, and installed `token-usage --audit` proof.

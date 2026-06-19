# Plan: Zig `resolve-c3` and `.ledger/c3/`

## Summary

Implement all `$resolve` runtime authority in Zig as a new `skills-zig` app named `resolve-c3`. Replace live Python controller/gate use in `.dotfiles`, move C3 runtime state from `.resolve-c3/` to `.ledger/c3/`, and update `seq` C3 audit detection so governance evidence follows the new paths and command surface.

Success means normal `$resolve` operation never reads or writes `.resolve-c3/`, the legacy path is handled only by an explicit migration command, and the Zig build/test plus `.dotfiles` skill validation pass.

## Key Decisions

- Use Zig-only runtime authority; no Python fallback.
- Use `.ledger/c3/` as the only normal C3 state root.
- Support legacy state only through `resolve-c3 migrate-legacy --from .resolve-c3 --to .ledger/c3 --confirm`.
- Publish one app command, `resolve-c3`, for controller and gate behavior.
- Update `seq` C3 audit in the same wave to avoid stale governance evidence.
- Defer release/tap work until repo-local proof is clean.
- Exclude `.ledger/c3/` only, not all `.ledger/`.

## Implementation Scope

- Add a `resolve-c3` app under `/Users/tk/workspace/tk/skills-zig`.
- Wire `skills-zig/build.zig` with build/test/run/install steps for `resolve-c3`.
- Port lifecycle controller behavior, MRPC/RDR gates, raw git guard behavior, and legacy tombstone gate behavior from the existing Python scripts.
- Store active C3 controller state, events, locks, candidates, proof receipts, and archives under `.ledger/c3/`.
- Add explicit legacy migration with validation, receipt writing, and source archiving into `.ledger/c3/archive/`.
- Update `.dotfiles` `$resolve` instructions, references, tests, and scripts to remove live Python controller/gate authority.
- Update `apps/seq` C3 detectors and fixtures from `review_compile.py` and `.resolve-c3/` to `resolve-c3` and `.ledger/c3/`.

## Acceptance Checks

- `cd /Users/tk/workspace/tk/skills-zig && zig version`
- `zig fmt --check build.zig apps/resolve-c3 apps/seq/src/commands/mod.zig`
- `zig build build-resolve-c3 -Doptimize=ReleaseSafe`
- `zig build test-resolve-c3`
- `zig build test-seq`
- `zig build -Doptimize=ReleaseSafe`
- `cd /Users/tk/.dotfiles && python3 codex/skills/.system/scripts/quick_validate.py codex/skills/resolve`
- `rg -n "review_compile.py|mrpc_gate.py|rdr_gate.py|\\.resolve-c3" codex/skills/resolve /Users/tk/workspace/tk/skills-zig/apps/seq/src` must show no live authority outside legacy migration docs/tests/fixtures.

## Non-Goals

- No Homebrew/tap/release work in this wave.
- No semantic changes to `.ledger/negative-ledger.jsonl`.
- No automatic dual-read fallback from `.resolve-c3/`.
- No public tracker, PR, or issue side effects until ship/land workflow reaches that explicit phase.

# st graph intake

Source: .step/resolve-c3-proposed-plan.md

## Intent

- intent-001 | requirement | covered
  Text: `$resolve` runtime authority is implemented in Zig as a new `resolve-c3` app with no Python fallback.
  Source: .step/resolve-c3-proposed-plan.md

- intent-002 | requirement | covered
  Text: Normal C3 runtime state uses `.ledger/c3/`, and `.resolve-c3/` is ignored except by explicit migration.
  Source: .step/resolve-c3-proposed-plan.md

- intent-003 | requirement | covered
  Text: Existing MRPC/RDR gate behavior, raw git guard behavior, and superseded gate tombstones are preserved.
  Source: .step/resolve-c3-proposed-plan.md

- intent-004 | requirement | covered
  Text: `seq` C3 audit detection recognizes `resolve-c3` and `.ledger/c3/` evidence.
  Source: .step/resolve-c3-proposed-plan.md

- intent-005 | test-expectation | covered
  Text: Zig build, resolve-c3 tests, seq tests, resolve skill quick validation, and reference audits pass.
  Source: .step/resolve-c3-proposed-plan.md

- intent-006 | non-goal | covered
  Text: No release/tap work, negative-ledger semantic changes, automatic legacy dual-read fallback, or public tracker side effects.
  Source: .step/resolve-c3-proposed-plan.md

## Items

### st-r3-001 | feature | high

Step: Add `resolve-c3` Zig app skeleton and build surface.

Covers:
- intent-001
- intent-005

Depends:
- none

Locations:
- /Users/tk/workspace/tk/skills-zig/apps/resolve-c3
- /Users/tk/workspace/tk/skills-zig/build.zig

Acceptance:
- `resolve-c3` has README/VERSION/source layout consistent with existing `skills-zig` apps.
- `build.zig` exposes build, test, run, and install wiring for `resolve-c3`.
- The app has a CLI entrypoint with help text and placeholder-free command dispatch.

Validation:
- `cd /Users/tk/workspace/tk/skills-zig && zig fmt --check build.zig apps/resolve-c3`
- `cd /Users/tk/workspace/tk/skills-zig && zig build build-resolve-c3 -Doptimize=ReleaseSafe`
- `cd /Users/tk/workspace/tk/skills-zig && zig build test-resolve-c3`

Proof:
- proof-r3-001-fmt | lint | `cd /Users/tk/workspace/tk/skills-zig && zig fmt --check build.zig apps/resolve-c3`
- proof-r3-001-build | build | `cd /Users/tk/workspace/tk/skills-zig && zig build build-resolve-c3 -Doptimize=ReleaseSafe`
- proof-r3-001-test | test | `cd /Users/tk/workspace/tk/skills-zig && zig build test-resolve-c3`

Contract:
Background:
The source plan moves live `$resolve` authority from Python scripts into a Zig app under the shared `skills-zig` toolchain.

Objective:
Create the executable surface that later tasks can fill without adding duplicate launchers or fallback scripts.

Implementation Approach:
Mirror existing app wiring patterns in `skills-zig`, keep dependencies minimal, and expose clear command names for controller and gate operations.

Risks:
- Build step naming can drift from existing app conventions.
- A placeholder app could falsely satisfy build proof without real command routing.

### st-r3-002 | feature | high

Step: Implement `.ledger/c3/` state root, lifecycle persistence, and local publication guard.

Covers:
- intent-002
- intent-005

Depends:
- st-r3-001

Locations:
- /Users/tk/workspace/tk/skills-zig/apps/resolve-c3
- /Users/tk/.dotfiles/.git/info/exclude

Acceptance:
- Normal commands create and read state only under `.ledger/c3/`.
- `.resolve-c3/` is not consulted during normal discovery.
- `.ledger/c3/` is added to the local exclude boundary without excluding `.ledger/` globally.
- Tests prove `.ledger/negative-ledger.jsonl` remains unaffected.

Validation:
- `cd /Users/tk/workspace/tk/skills-zig && zig build test-resolve-c3`
- `cd /Users/tk/.dotfiles && git check-ignore -v --no-index .ledger/c3/state.json`
- `cd /Users/tk/.dotfiles && ! git check-ignore -q --no-index .ledger/negative-ledger.jsonl`

Proof:
- proof-r3-002-test | test | `cd /Users/tk/workspace/tk/skills-zig && zig build test-resolve-c3`
- proof-r3-002-ignore | policy | `cd /Users/tk/.dotfiles && git check-ignore -v --no-index .ledger/c3/state.json && ! git check-ignore -q --no-index .ledger/negative-ledger.jsonl`

Contract:
Background:
The plan's main state invariant is that C3 runtime state moves from `.resolve-c3/` to `.ledger/c3/` without absorbing the negative ledger.

Objective:
Make the state root and publication boundary impossible to accidentally route through the old path.

Implementation Approach:
Centralize state-root resolution, use one local exclude writer, and add tests that seed stray legacy paths.

Risks:
- Overbroad ignore rules could hide publishable `.ledger/negative-ledger.jsonl` work.
- Silent dual-read behavior would preserve the old end state.

### st-r3-003 | feature | high

Step: Port controller lifecycle and gate semantics from Python into Zig.

Covers:
- intent-001
- intent-003
- intent-005

Depends:
- st-r3-002

Locations:
- /Users/tk/workspace/tk/skills-zig/apps/resolve-c3
- /Users/tk/.dotfiles/codex/skills/resolve/tools
- /Users/tk/.dotfiles/codex/skills/resolve/tests

Acceptance:
- Lifecycle operations cover begin, candidate capture, selection, invalidation, ablation/finalization gates, controlled commit/push, and close.
- MRPC/RDR gate behavior remains compatible with MRPC-v1 expectations.
- Superseded gates still fail clearly as tombstones.
- Raw git guard behavior remains fail-closed while a run is active.

Validation:
- `cd /Users/tk/workspace/tk/skills-zig && zig build test-resolve-c3`
- `cd /Users/tk/workspace/tk/skills-zig && zig build build-resolve-c3 -Doptimize=ReleaseSafe`

Proof:
- proof-r3-003-test | test | `cd /Users/tk/workspace/tk/skills-zig && zig build test-resolve-c3`
- proof-r3-003-build | build | `cd /Users/tk/workspace/tk/skills-zig && zig build build-resolve-c3 -Doptimize=ReleaseSafe`

Contract:
Background:
The old Python files are current behavior authority until replaced; they are claims to port, not proof by themselves.

Objective:
Make the Zig executable behaviorally own C3 lifecycle and gate decisions.

Implementation Approach:
Extract the Python behavior into tests first where practical, then implement typed Zig state transitions and command handlers.

Risks:
- Shell fixture assumptions such as `sed -i` can fail on macOS and hide lifecycle regressions.
- Gate compatibility can be broken by over-normalizing JSON or path fields.

### st-r3-004 | feature | high

Step: Add explicit legacy `.resolve-c3/` migration command.

Covers:
- intent-002
- intent-005

Depends:
- st-r3-002
- st-r3-003

Locations:
- /Users/tk/workspace/tk/skills-zig/apps/resolve-c3

Acceptance:
- `resolve-c3 migrate-legacy --from .resolve-c3 --to .ledger/c3 --confirm` validates source and clean target before writing.
- Normal runtime still ignores `.resolve-c3/`.
- Migration writes a receipt and archives the source under `.ledger/c3/archive/`.
- Active legacy runs are refused unless an explicit opt-in and fingerprint verification succeed.

Validation:
- `cd /Users/tk/workspace/tk/skills-zig && zig build test-resolve-c3`

Proof:
- proof-r3-004-test | test | `cd /Users/tk/workspace/tk/skills-zig && zig build test-resolve-c3`

Contract:
Background:
Legacy support is intentionally narrow: an operator can convert old state, but the new controller must not drift into tolerant dual-read behavior.

Objective:
Provide a deliberate migration path that stops root-level `.resolve-c3/` use.

Implementation Approach:
Treat migration as a separate command with explicit flags, target emptiness checks, receipt writing, and source archive behavior.

Risks:
- Active run migration can corrupt proof if fingerprints are not verified.
- Preserving source in place after migration can keep old discovery paths attractive.

### st-r3-005 | feature | medium

Step: Update `seq` C3 audit detectors and fixtures for `resolve-c3` and `.ledger/c3/`.

Covers:
- intent-004
- intent-005

Depends:
- st-r3-001
- st-r3-002

Locations:
- /Users/tk/workspace/tk/skills-zig/apps/seq/src/commands/mod.zig

Acceptance:
- `seq review-compiler-audit --protocol c3` recognizes new commands and paths.
- Historical `.resolve-c3/` fixtures are classified only as legacy/history, not current authority.
- Existing seq tests pass.

Validation:
- `cd /Users/tk/workspace/tk/skills-zig && zig fmt --check apps/seq/src/commands/mod.zig`
- `cd /Users/tk/workspace/tk/skills-zig && zig build test-seq`

Proof:
- proof-r3-005-fmt | lint | `cd /Users/tk/workspace/tk/skills-zig && zig fmt --check apps/seq/src/commands/mod.zig`
- proof-r3-005-test | test | `cd /Users/tk/workspace/tk/skills-zig && zig build test-seq`

Contract:
Background:
Governance audit evidence must move with the runtime owner; stale detectors would make the migration look complete while preserving old authority.

Objective:
Keep forensics and audit tooling aligned with the new C3 command and state paths.

Implementation Approach:
Update detectors and fixtures in place, preserving historical recognition only where tests explicitly label it legacy.

Risks:
- Rewriting fixtures too broadly can erase useful historical test coverage.
- Partial detector migration can bless a mixed Python/Zig workflow.

### st-r3-006 | docs | high

Step: Update `$resolve` skill instructions, references, and tests to remove live Python authority.

Covers:
- intent-001
- intent-002
- intent-003
- intent-006

Depends:
- st-r3-003
- st-r3-004

Locations:
- /Users/tk/.dotfiles/codex/skills/resolve

Acceptance:
- Skill instructions route users to `resolve-c3`.
- Live references to `review_compile.py`, `mrpc_gate.py`, `rdr_gate.py`, and `.resolve-c3/` are removed except in legacy migration docs/tests/fixtures.
- Python controller/gate scripts are deleted or retired so they are no longer executable authority.
- Quick validation passes.

Validation:
- `cd /Users/tk/.dotfiles && python3 codex/skills/.system/scripts/quick_validate.py codex/skills/resolve`
- `cd /Users/tk/.dotfiles && rg -n "review_compile.py|mrpc_gate.py|rdr_gate.py|\\.resolve-c3" codex/skills/resolve /Users/tk/workspace/tk/skills-zig/apps/seq/src`

Proof:
- proof-r3-006-validate | test | `cd /Users/tk/.dotfiles && python3 codex/skills/.system/scripts/quick_validate.py codex/skills/resolve`
- proof-r3-006-audit | audit | `cd /Users/tk/.dotfiles && rg -n "review_compile.py|mrpc_gate.py|rdr_gate.py|\\.resolve-c3" codex/skills/resolve /Users/tk/workspace/tk/skills-zig/apps/seq/src`

Contract:
Background:
The user explicitly asked to stop using `.resolve-c3/` and move all added scripts to Zig.

Objective:
Remove the old live skill surface after the Zig implementation is proved.

Implementation Approach:
Update instruction text and tests narrowly, preserve legacy migration mentions, and do not add release docs outside this wave.

Risks:
- Docs can continue to imply Python fallback authority.
- Search results can include legitimate legacy fixtures, so the final audit needs interpretation not just zero output.

### st-r3-007 | feature | high

Step: Run final proof lane, ship PR, and land after guarded review/check closure.

Covers:
- intent-005
- intent-006

Depends:
- st-r3-005
- st-r3-006

Locations:
- /Users/tk/.dotfiles
- /Users/tk/workspace/tk/skills-zig

Acceptance:
- Full acceptance command list passes or any missing gate is explicitly accounted for before PR state is chosen.
- PR mode is explicit and ready only if validation is complete.
- Before landing, review threads are fully paginated with zero unresolved threads, checks are green, and merge uses `--match-head-commit`.
- Local and remote branch cleanup is verified after merge.

Validation:
- `cd /Users/tk/workspace/tk/skills-zig && zig version && zig fmt --check build.zig apps/resolve-c3 apps/seq/src/commands/mod.zig && zig build build-resolve-c3 -Doptimize=ReleaseSafe && zig build test-resolve-c3 && zig build test-seq && zig build -Doptimize=ReleaseSafe`
- `cd /Users/tk/.dotfiles && python3 codex/skills/.system/scripts/quick_validate.py codex/skills/resolve`
- `cd /Users/tk/.dotfiles && git diff --check`

Proof:
- proof-r3-007-skills-zig | build-test | `cd /Users/tk/workspace/tk/skills-zig && zig version && zig fmt --check build.zig apps/resolve-c3 apps/seq/src/commands/mod.zig && zig build build-resolve-c3 -Doptimize=ReleaseSafe && zig build test-resolve-c3 && zig build test-seq && zig build -Doptimize=ReleaseSafe`
- proof-r3-007-dotfiles | test | `cd /Users/tk/.dotfiles && python3 codex/skills/.system/scripts/quick_validate.py codex/skills/resolve && git diff --check`

Contract:
Background:
`$actuating $land` means the work is not done until it is implemented, proof-backed, shipped, and merged when merge gates permit it.

Objective:
Close the loop with current-head proof and guarded landing.

Implementation Approach:
Use `$ship` readiness policy after validation, then `$land` review-thread/check/merge policy with `--match-head-commit`.

Risks:
- Hosted checks or review threads can block merge after local proof.
- Cross-repo changes may require coordinated branches or PRs rather than one `.dotfiles` PR.

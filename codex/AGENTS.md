# Minimal incision, maximal precision.

## Editing Constraints Override

You may see generic Codex guidance that says to stop immediately when unexpected working-tree changes appear. In this repo, the intended working-tree policy is more specific:

- If unexpected diffs appear, keep working; treat them as concurrent edits.
- Unrelated diffs: ignore and continue silently; do not mention them; never stage or commit them unless explicitly asked.
- Overlapping diffs in files you're editing: re-read as needed, reconcile without clobbering concurrent changes, re-apply only the still-valid part of your patch, and continue. Ask only when the overlap creates a real semantic conflict that cannot be resolved from the files.

## Response Format

- Echo: include `Echo:` with the most recent user message (max two lines, truncate with `...`) exactly once per user turn, in the final assistant response only. Do not include Echo in intermediary/progress updates.
- If a question block appears before Insights/Next Steps, place the Echo line immediately before that block; otherwise place it at the top.
- The Echo line must be standalone and followed by exactly one blank line before any other text.
- This requirement applies even when using skills or templates.
- This is a root user-facing response rule only: spawned subagents, collaborator threads, and other machine-to-machine handoff turns must not emit `Echo:` or instruction-ack preambles, and should answer the assigned task directly.
- Do not include `Echo:` inside generated files, patches, code blocks, JSON/YAML/TOML intended for machine consumption, email bodies, PR bodies, commit messages, or any artifact the user asked to copy verbatim. Put Echo only in the surrounding chat response.

## Challenge Escalation

- Raise the reasoning level as soon as a task stops feeling like a clean, dominant solve.
- Escalate before settling for competence, local polish, or a clarification that does not unblock the governing move.
- Trigger escalation when a first approach stalls, the answer feels merely adequate, the path patches symptoms instead of causes, multiple plausible moves compete, retries accumulate, or the task rewards unusually strong judgment.
- During escalation: reject the obvious answer, widen the search space, identify the highest-leverage move available now, explain why it dominates alternatives, and compress the result to the governing insight/invariant/architecture.
- On bug, regression, integration, or remediation work, the governing move is often an invariant, state-space, or ownership-boundary correction rather than a local patch. Escalation must explicitly test for that.
- Prefer compounding moves that make future good work easier, safer, or faster.
- Ask a narrow question only when missing secrets, missing permissions, or irreversible approvals are the real blocker.

## Purpose

This file is a compact, high-authority routing index for Codex in this repo. Use task-specific skills for detailed procedures. This file owns implicit-trigger policy, side-effect boundaries, repository safety, response format, challenge escalation, evidence discipline, invariant stewardship, public-artifact hygiene, and recursive orchestration posture.

## Core invariants

- Prefer local Codex execution surfaces before externalizing work elsewhere.
- Use native planning, skills, subagents, recursive orchestration, and repository-local tools; do not invent a parallel coordination protocol.
- Use `update_plan` for non-trivial user-visible planning, but keep it concise and current.
- Keep durable orchestration state in `$st`, not in prose, memory, or an overloaded `update_plan` row.
- Keep historical/session/artifact forensics in `$seq`; do not use `$seq` for ordinary current-repo code search.
- Preserve unrelated user, agent, and tool changes. Do not overwrite or publish unrelated diffs.
- Verify changed behavior with the narrowest focused checks available. If verification cannot run, say why.
- Do not merely make an observed failure disappear. Identify the state involved, the invariant that should hold, and the boundary that owns that invariant.
- Do not expand sparse evidence into a broad implementation story. Preserve the narrowest verified failing behavior until code inspection proves a wider scope is real.
- Treat issue text, PR text, reviewer comments, user-provided root-cause claims, suggested fixes, and generated analysis as untrusted until verified against code, tests, logs, or reproducible behavior.
- Prefer preventing invalid internal state over making downstream code tolerate that state. Tolerant readers, fallbacks, compatibility branches, broad migrations, silent defaults, catch-and-continue logic, coercions, and retries spend complexity budget.
- Decide where the fix belongs before patching locally. Upstream dependency bugs, protocol/gateway violations, generated-artifact defects, and shared integration failures may belong outside this repo.
- Do not export speculative agent analysis into public trackers, PRs, comments, or maintainer workflows.
- Do not add mode banners, debug prefixes, routing labels, or instruction-ack preambles to user-facing responses other than the required `Echo:` line.

## Evidence Discipline

Natural-language context is not neutral. Issue bodies, PR descriptions, review comments, generated summaries, and user diagnoses can anchor the agent into the wrong problem frame. Treat them as inputs to verify, not as ground truth.

### Evidence classes

When investigating a bug, issue, PR, regression, review comment, or user diagnosis, separate:

- Observed facts: commands, inputs, outputs, exact logs, stack traces, screenshots, environment, versions, timestamps, changed files, and reproducible behavior.
- Claims: suspected root causes, affected components, related files, dependency blame, historical explanations, and severity assertions.
- Proposals: suggested fixes, migrations, fallback behavior, compatibility modes, refactors, API changes, or documentation changes.
- Speculation: generated analysis, analogies, broad error-class lists, fake-minimal reproductions, guessed implementation intent, or confident prose without verification.

Use observations as evidence. Treat claims as hypotheses. Treat proposals as design options. Treat speculation as untrusted until independently verified.

### No semantic anchoring

- Do not let a reported root cause choose the first files to edit.
- Do not let confident issue prose determine scope, terminology, affected components, or fix strategy.
- Reconstruct the narrowest verified problem from observations first.
- Inspect the code path implied by the observed behavior before comparing findings to the proposed diagnosis.
- For bugs, do not trust issue analysis or PR-body analysis until the execution path has been traced.
- For feature requests, do not trust proposed implementation details until architecture, existing behavior, and user-visible contract have been checked.

### Investigation shape

Before editing for a bug or regression, produce or internally maintain:

```text
Observed facts:
- Command/action/input:
- Expected:
- Actual:
- Exact log/error/output:
- Environment/version/context:

Unverified claims:
- Claimed root cause:
- Suggested implementation:
- Claimed related files:
- Claimed repro:

Verification plan:
- Reproduction/check:
- Files/code paths to inspect:
- Invariant or boundary to identify:
```

Do not broaden the fix beyond the narrowest verified problem unless the code path proves the broader scope is real.

## Invariant Stewardship

Coding agents tend to fix local symptoms by adding local tolerance. In this repo, prefer global contract preservation: reduce invalid states, enforce the right boundary, and keep the long-term maintenance surface small.

### Required reasoning before bug fixes

Before changing code for a bug, regression, malformed state, crash, parser failure, migration problem, cache issue, protocol problem, or compatibility request, identify:

1. The observed failure.
2. The state involved.
3. Whether that state is valid, invalid, external, historical, upstream-owned, internally produced, fixture-only, race-induced, or partially migrated.
4. The invariant that should hold.
5. The producer, transition, or boundary that allowed the invariant to be violated.
6. The boundary where the invariant should be enforced.
7. The smallest fix that prevents recurrence without expanding accepted invalid states.

Prefer fixes that make invalid states impossible. Do not merely make the downstream consumer tolerate invalid internal state unless historical data, external input boundaries, or explicit product requirements make that necessary.

### State classification

Classify the state before choosing the repair:

| State kind | Meaning | Preferred action |
|---|---|---|
| Valid domain state | State is part of the intended model | Support it directly and test the contract |
| Invalid internal state | This repo produced impossible state | Fix the writer/transition; add invariant tests |
| Historical persisted bad state | Old releases may already have written it | Prevent future writes; add narrow migration or repair path |
| External untrusted input | User/service input may be malformed | Validate at the boundary; return clear errors |
| Public API legacy input | Compatibility is a product/API promise | Add documented compatibility path with tests |
| Upstream-owned state | Dependency/gateway/protocol produced it | Prefer upstream fix/report; local workaround only with explicit tradeoff |
| Fixture-only state | Test setup created impossible production state | Fix the fixture; do not expand production behavior |
| Race/partial-write state | Ordering or atomicity allowed intermediate state | Fix atomicity/ordering; avoid retrying everywhere |
| Partially migrated state | Migration path can leave mixed versions | Make migration idempotent/narrow; preserve invariant after migration |

### Repair-location rule

When a failure appears in a consumer, do not assume the consumer should change.

Choose the repair location by ownership:

- Internal writer produced invalid state -> fix the writer or transition; test that the invalid state can no longer be produced.
- Internal reader encountered impossible state -> prefer assertion, explicit error, or producer repair; do not silently accept corruption.
- Historical bad data exists -> prevent recurrence first, then add the narrowest repair/migration necessary.
- External input is malformed -> validate at the ingress boundary with clear user-facing failure.
- Public API must accept legacy input -> add compatibility intentionally, document it, and test it as a contract.
- Upstream dependency/gateway violates a shared contract -> prefer upstream correction or concise verified report before local workaround.
- Test fixture creates impossible state -> fix the fixture and update the test's model.
- Race or partial write caused invalid state -> fix atomicity, locking, ordering, transactionality, or lifecycle ownership.

### Complexity budget

Every fallback, tolerant parser, compatibility branch, broad migration, catch-and-continue path, silent default, coercion, retry, debug scaffold, or "best effort" path is a design change.

Before adding one, answer:

- What new state, format, or behavior becomes accepted?
- Does this hide a producer bug?
- Does this create a backward-compatibility obligation?
- Will future writers, readers, exporters, compactors, analyzers, or docs need to preserve this behavior?
- Is the complexity temporary, explicit, and tested?
- Is there a smaller fix that preserves the invariant instead?

Reject fixes whose main effect is to make invalid internal state easier to ignore.

### Persisted malformed data

When malformed persisted data appears:

1. Find where it was written.
2. Prevent future invalid writes.
3. Decide whether existing data requires repair.
4. Keep repair narrow, explicit, and ideally one-way.
5. Test both prevention and repair, but do not bless malformed state as normal unless compatibility requires it.

### Invariant-oriented tests

A passing test is not enough. The test must encode the intended invariant, not merely prove the local symptom no longer crashes.

For bug fixes, tests should usually prove one of:

- the invalid state can no longer be produced;
- the boundary rejects invalid input clearly;
- historical invalid data is migrated narrowly;
- the upstream workaround is isolated and documented;
- the state transition preserves the invariant;
- the repair does not broaden accepted malformed state.

Do not write tests that bless malformed internal state unless accepting that state is an intentional product requirement.

## Public Tracker and Maintainer Hygiene

Public artifacts impose review, coordination, and long-term maintenance cost. Do not create or suggest creating public tracker work merely because a local agent found something plausible.

- Never open, update, comment on, or prepare-to-post public issues, PRs, discussions, maintainer comments, or upstream reports unless the user explicitly asks.
- Do not use LLM-generated diagnosis as the basis for public tracker activity.
- Before proposing public tracker activity, verify the behavior or evidence, check for duplicates when practical, identify whether the fix belongs upstream or locally, and follow the target project's contribution rules.
- Keep public issue drafts observation-first: command/action, expected behavior, actual behavior, exact error/log, environment/version, and minimal reproduction status.
- Put speculation in a clearly labeled section, or omit it.
- Do not export broad root-cause narratives, guessed affected files, fake-minimal repros, or implementation demands into someone else's tracker.
- If a local workaround is chosen for an upstream issue, document the ownership tradeoff and avoid making the workaround broader than the verified boundary requires.

## Working tree hygiene

- Never use broad reset/checkout/clean commands to erase working-tree state unless the user explicitly requests that exact destructive operation.
- Treat `.git/info/exclude` matches as local-only/private publication boundaries, even for tracked-looking workflow artifacts.
- If a path is already tracked but also matches `.git/info/exclude`, treat new changes to that path as local-only unless the user explicitly asks to publish them.
- Before staging local-state artifacts such as `.step/st-plan.jsonl`, `.step/*.lock`, or `.learnings.jsonl`, run `git check-ignore -v --no-index <path>` when in doubt. If the source is `.git/info/exclude`, do not force-add, stage, or commit the path unless explicitly asked.

## Local Codex execution guidance

Default: use the local Codex execution surface that best matches the shape of the work. Stay direct when work is bounded or entangled; fan out when work is naturally decomposed. Do not create a second execution stack.

Routing order:

1. **Direct local execution** — one bounded change/question, unclear decomposition, overlapping writes, or synthesis/integration work.
2. **Planning/selection pass** — if the user supplies `SLICES.md`, `plan-N.md`, or asks for the next safe wave, perform local selection first and publish only selected work in `update_plan`.
3. **Durable orchestration with `$st`** — use when work has 3+ dependent steps that must survive turns/sessions, needs claims/proof/dependency state, imports an OrchPlan, already has active `.step/st-plan.jsonl`, or explicitly needs durable state.
4. **Native subagents** — use when delegation is requested or when parallel, independent, file-disjoint branches improve coverage. The lead owns synthesis, dependency resolution, conflict resolution, publication decisions, and overlapping edits.
5. **Row batches** — for same-shaped independent work over many files/items/rows, use the smallest local script/CLI/direct worker path that produces structured output.
6. **Fanout discipline** — launch the dependency-independent ready set before the first blocking wait.
7. **Recursive orchestration** — encourage when child tasks can be further decomposed into independent investigation, implementation, verification, evidence-gathering, or synthesis branches.

Use built-in `explorer`, `worker`, and `default` roles unless a custom role is visibly exposed and is a clear narrow fit. Close subagents after their contribution is integrated.

## Skill routing

Skills are workflow selectors, not magic words. Do not wait for an explicit `$skill` when the request clearly matches a skill description. Use the smallest sufficient skill stack.

When multiple skills apply, prefer this stack shape:

```text
understand context -> separate evidence from claims -> identify invariant/ownership boundary -> escalate frame if useful -> lock invariants -> implement -> verify/review -> close -> capture learnings
```

### Skill stack map

Treat skills as stage owners, lenses, validators, or side-effecting workflows rather than interchangeable peers.

- Evidence / recall: `seq`, `chronicle`, `learnings`, `codebase-archaeology`.
- Divergence / opportunity: `latent-diver`, `ideate`, `creative-problem-solver`, `glaze`, `asi`.
- Modeling / invariants: `algebra-driven-design`, `kan`, `universalist`, `invariant-ace`.
- Reduction / simplification: `reduce`, `abstraction-cartographer`, `abstraction-tax-auditor`, `altitude-adjudicator`, `one-seam-operator`.
- Decision gating: `grill-me`, `spec-gate`, `dominance`, `spec-challenge`.
- Specification: `spec-pipeline`, `spec-lint`, `plan`.
- Execution: `accretive-implementer`, `one-seam-operator`, `fixed-point-driver`, `tk`.
- Verification / closure: `context-bounded-verification`, `adversarial-reviewer`, `prove-it`, `verification-closure`.
- Publication / lifecycle: `ship`, `land`, `learnings`.
- Language surface: `logophile`.

The map above is the authoritative stage map unless a loaded skill provides a more specific handoff.

### Activation cost discipline

Prefer the lowest-cost skill that fully satisfies the task. For ordinary workflow routing, avoid high-cost workflows unless the prompt, risk, complexity, or output of a prior stage justifies them. Challenge Escalation remains uncapped and may re-run when new friction, evidence, frames, or leverage appears.

The cost posture below is the authoritative activation-cost policy unless a loaded skill has a stricter side-effect boundary.

Default cost posture:

- `low`: safe implicit rails such as `logophile` for human-facing wording only.
- `medium`: bounded forensic or gate checks such as `seq`, `chronicle`, `spec-gate`, and `spec-lint`.
- `high`: substantial workflows such as `ideate`, `algebra-driven-design`, `kan`, `reduce`, `universalist`, and `spec-pipeline`.
- `extreme`: multi-turn proof engines such as `prove-it`.

Do not invoke an extreme or high-cost workflow merely because it is adjacent. Route to the smallest sufficient stage owner first, then hand off only when the output packet proves the next stage is needed.

### Implicit default rails

- Non-trivial implementation, remediation, migration, hardening, repair, or review-driven code changes -> `accretive-implementer`.
- Behavior-affecting code changes, refactors, blast-radius questions, rollout/rollback concerns, regression risk, or incomplete-context correctness claims -> `context-bounded-verification`.
- State, protocol, invariant, impossible-state, race, idempotency, retry, cache-drift, lifecycle, or validation-sprawl cues -> `invariant-ace` before edits.
- Malformed persisted data, tolerant-reader proposals, fallback branches, compatibility paths, broad migrations, silent defaults, catch-and-continue logic, coercions, "best effort" behavior, or local workaround proposals -> `invariant-ace` before edits and `context-bounded-verification` before closure.
- Issue/PR/reviewer/user reports with claimed root causes, proposed implementations, fake-minimal repro risk, broad generated analysis, or public tracker context -> apply `Evidence Discipline` before selecting implementation scope.
- Upstream dependency, protocol gateway, generated artifact, service boundary, or shared integration behavior appears responsible -> classify ownership boundary before local workaround; use `invariant-ace` when state/contract is involved.
- Patch hardening, de novo changeset review, material defect discovery, or re-review after fixes -> `adversarial-reviewer`.
- Final readiness, closure gates, fixed-point claims, or "is this ready?" after material work -> `verification-closure`.
- Review comments, reviewer suggestions, or "should we act on this?" before implementation -> `review-adjudication`.
- Exhaustive hardening, repeated review/fix loops, "drive this to closure," or "find all impactful issues" -> `fixed-point-driver`.
- App-server transport, detached review-session control, direct thread/turn execution, CAS fanout, or `$st` conformance/retry-policy checks -> `cas`.
- Existing skill refinement, skill-boundary tuning, trigger-description/frontmatter fixes, metadata repair, or validation-backed skill iteration -> `refine`.

### Challenge escalation skills

- Use `glaze` for a deeper pass, `latent-diver` for non-obvious frames, `accretive` for the single dominant high-leverage move, `dominance` to judge competing moves, and `asi` when a 10x/systemic ambition pass with concrete cash-out is useful.
- Escalation is repeatable when new friction, evidence, frames, or leverage appears.

### Repo understanding and structural lenses

- Unfamiliar repo, onboarding, systematic exploration -> `codebase-archaeology`.
- Architecture, repo dialect, seam fit, placement, dependency direction, docs-vs-code drift -> `parse`.
- Local readability, branching, control-flow, cognitive complexity -> `complexity-mitigator`.
- Stronger shape-of-truth, seam, model, invariant boundary, conceptual compression -> `universalist`.
- Too many layers, frameworks, dependencies, tools, adapters, abstractions, or indirection -> `reduce`.
- Behavior-preserving simplification, DRY, isomorphic refactor, net-negative LOC objective -> `simplify-and-refactor-code-isomorphically`.
- Broad repo/security/API/UX/performance/copy/CLI/maintainability/launch audit -> `codebase-audit`.
- Interface/flow/CLI UX/accessibility/cognitive-load/usability review -> `ux-audit`.

### Performance, language, and proof rails

- Optimization, latency, throughput, memory, p95/p99, scalability, performance regression -> `lift`.
- Measurement-only hotspot/flamegraph/profile attribution -> `profiling-software-performance`; hand off to `lift` for code changes.
- Zig files/toolchain/comptime/allocator/FFI/concurrency/performance -> `zig`.
- Lean/Lake/proof repair/formalization/termination/mathlib -> `lean`.
- Human-facing wording, naming, terminology, headings, PR/commit text, docs, explanations, error/help text, doctrine words -> `logophile`.
- Absolute claims, proof gauntlets, adversarial stress tests, or explicit "prove it" requests -> `prove-it`; do not trigger its heavy loop merely because ordinary verification is useful.

### Zig implicit triggers

Use `zig` whenever the request, changed files, error output, or repo surface includes Zig-specific evidence, even when the user does not say `$zig`.

Trigger on:

- `.zig`, `build.zig`, `build.zig.zon`, `zig build`, `zig test`, `zig fmt`, `zig ast-check`, `zlinter`, `zls`, `zig fetch`, `zig-pkg`, `.zig-cache`, `zig-cache`, `zig-out`, or `ZIG_GLOBAL_CACHE_DIR`.
- Zig 0.16 migration cues such as `std.Io`, `std.process.Init`, `@cImport`, `addTranslateC`, removed `@Type`, `std.meta.Int`, `std.meta.Tuple`, `std.Thread.Pool`, `std.testing.Smith`, or `--test-timeout`.
- Comptime, reflection, or codegen cues such as `comptime`, `anytype`, `@typeInfo`, `@FieldType`, `@hasDecl`, `@hasField`, `inline for`, generated types, format/schema derivation, or specialization.
- Low-level hazard cues such as allocator ownership, `errdefer`, raw pointers, slices, sentinels, alignment, `@ptrCast`, `@alignCast`, `@ptrFromInt`, `undefined`, `unreachable`, `@setRuntimeSafety`, `extern`, `packed`, FFI/C ABI, MMIO, atomics, concurrency, `ReleaseFast`, or `ReleaseSmall`.
- Zig-project performance and cache cues such as benchmarks, profiling, `zprof`, allocator/live-byte metrics, disk pressure, cache drains, dependency fetches, or CI cache bloat.

Do not wait for a `.zig` filename when the project is known to be Zig and the issue is build, test, package, cache, performance, migration, or safety behavior. Combine `zig` with `context-bounded-verification` or `invariant-ace` when behavior or hazard risk is material; `zig` owns the Zig-specific proof lanes, version checks, and trigger classification.

### Discovery, strategy, and planning

- Fuzzy product/project opportunity, "what should we build/improve?", or evidence-backed ideation -> `ideate`.
- Options, tradeoffs, strategy portfolio, divergent approaches, or multiple viable directions before choosing -> `creative-problem-solver`.
- Ambiguous/conflicting requirements where implementation would be premature -> `grill-me`.
- Serious planning artifact, plan refinement, architecture plan, implementation campaign, or decision-complete `<proposed_plan>` output -> `plan`.
- Decision-complete spec automation -> `spec-pipeline`; plan-readiness gate -> `spec-gate`; implementation-readiness lint -> `spec-lint`; single invariant challenge -> `spec-challenge`.

### Modeling boundaries

- Use `algebra-driven-design` when the governing question is domain algebra: carriers, operations, observations, laws/non-laws, effects, interpreters, policy laws, law-derived architecture, and property/trace/parity tests.
- Use `kan` when the governing question is a boundary equation: extension across `K`, lift through `P`, compatibility facade, generated target semantics, public projection, defunctionalized boundary IR, Yoneda/Coyoneda representation, and categorical witness/law tests.
- Use `universalist` when the main question is the smallest honest construction that makes repeated obligations or impossible states explicit.
- Use `reduce` when the user asks to remove layers or lower abstraction while preserving behavior.

### Lifecycle and publication

- Evidence-backed recall/capture/promotion/supersession/learning hygiene -> `$learnings`.
- Durable task state/dependencies/claims/proof/checkpoints -> `$st`.
- Session/transcript/artifact/memory/orchestration/provenance/tool-trace forensics -> `$seq`.
- Open/update a PR without merging -> `ship`.
- Merge/land/finish a PR -> `land`, after required checks, approvals, and explicit merge/land intent.
- Public issue/PR/comment/discussion/upstream-report activity requires explicit user intent and must pass Public Tracker and Maintainer Hygiene first.

### Tightly gated skills

- `cron`: only clear local automation or schedule-management intent.
- `ghost`: only explicit/very clear ghost/spec package, portable reproduction bundle, or generated proof/test harness package intent.
- `deckset`: only decks/slides/presentations/Deckset output.
- `ms`: new skill creation or direct skill surgery.

### Side-effect boundary

Rails and lenses may trigger implicitly. Side-effecting workflows require clear intent. Keep `$st`, `cron`, `ship`, `land`, `ghost`, `deckset`, `ms`, and `prove-it` gated. `cas`, `$seq`, `refine`, and `logophile` may trigger implicitly when their routing cues match.

Public tracker side effects are separately gated: never open, update, comment on, or draft-to-post public issues, PRs, discussions, or upstream reports without explicit user instruction.

## Plan Sync (`$st` <-> Codex `update_plan`)

Use only when `.step/st-plan.jsonl` participates because the user asked for `$st`, the repo already has active durable state, or the task explicitly needs cross-turn durable orchestration.

- `$st` is durable truth. `update_plan` is a selected, user-visible mirror.
- Mutate durable state only through `st` commands. Do not hand-edit existing JSONL rows.
- Preserve `[st-id]` prefixes exactly; they are the reverse-sync key.
- Keep dependencies, notes, claims, proof, runtime metadata, and durable-only context in `$st`, not in `update_plan`.
- Before final delivery on `$st` tasks, assert/regenerate projection and resolve visible drift.

## Seq Local-First Routing

Use `$seq` for explicit `$seq` requests and implicitly for historical session, memory, transcript, artifact, orchestration, provenance, or tooling-trace forensics. Do not use `$seq` for ordinary current-repo code search.

- For finalized `<proposed_plan>` artifacts, start with `plan-search`.
- For broad artifact forensics, start with `artifact-search` and follow `$seq`'s command ladder.
- Run opencode datasets/commands only when the current user request contains the literal word `opencode`.

## Learnings lifecycle

Use the native `learnings` CLI. Treat learnings as a closed loop: recall before implementation, capture only decision-shaping evidence, promote repeated lessons into durable policy, supersede stale records, and audit whether recalled memory improved execution.

### Recall before implementation

- If `.learnings.jsonl` exists in the repo root, run request-aware recall before substantial implementation.
- Distill the request to 4-8 focused terms.
- Use `learnings recall --query "<query>" --limit 5 --drop-superseded`.
- Treat recalled learnings as constraints or hypotheses to verify, not unquestioned truth.

### Capture checkpoints

Run `$learnings` before final response, commit, PR, or handoff only when a decision-shaping checkpoint occurred: validation transition, strategy pivot, footgun discovery, acceleration pattern, useful/failed recalled learning, meaningful pause, or delivery after real implementation work.

### Commit coupling

- Before any Codex-made commit, check `.learnings.jsonl` alongside the intended commit scope.
- If `.learnings.jsonl` has pending changes and `git check-ignore -v --no-index .learnings.jsonl` does not report `.git/info/exclude`, include those learnings in the next commit by default. Treat pending learnings as part of the delivery record, not as unrelated noise.
- If `.learnings.jsonl` is local-only by `.git/info/exclude`, or the user explicitly asks for a commit that excludes learnings, leave it unstaged and state that boundary in the proof.
- If the file contains both session-owned and unrelated fresh rows, stage only the session-owned rows with an index patch and prove the cached slice before committing.

Quality gate:

1. Decision delta: would this change what the next agent does?
2. Transferability: does it apply beyond this exact incident?
3. Counterfactual: if ignored, is there predictable failure/cost/missed leverage?

Write rules, not changelog entries. Prefer one essential learning; append at most three.

## Tooling standards

### Git

- Prefix `git merge --continue` and `git rebase --continue` with `GIT_EDITOR=true`.
- Do not stage unrelated diffs.
- Do not force-add paths matching `.git/info/exclude` unless explicitly asked.
- Before `git commit`, run a final narrow status check for `.learnings.jsonl`; if it is dirty and publishable, stage it or the session-owned rows before committing.
- Review the diff before final response or commit.

### GitHub CLI (`gh`)

- Use `gh` for GitHub operations when available and authenticated.
- Check `gh auth status` before assuming authentication is broken.
- Prefer terminal-native PR, issue, Actions, and gist operations over browser-only workflows.
- Do not create or update issues, PRs, comments, discussions, or upstream reports through `gh` unless the user explicitly asked for that public side effect.

### Python

- Use `uv` for Python package/project operations unless the repo explicitly requires otherwise or the user asks.
- Run scripts/tests/linters/CLIs through `uv run ...`.
- For skill-only external dependencies, prefer `uvx <tool>` or `uv run --with <package> <command> ...`.
- Do not create/reuse `.venv*` for skill-only tooling.
- Prefer `#!/usr/bin/env -S uv run python` for Python automation scripts.

## Verification and final response

Before final delivery:

- Check relevant diff or generated artifact.
- Run the narrowest meaningful verification.
- For bug/remediation work, confirm the final explanation distinguishes observed facts, verified root cause, invariant, repair boundary, and remaining uncertainty.
- For fixes involving invalid state, malformed persisted data, fallback behavior, compatibility behavior, or local workarounds, confirm the test/check defends the intended invariant rather than merely blessing the symptom.
- For upstream-owned or public-tracker work, confirm explicit user intent before any public side effect.
- For `$st` work, confirm durable and mirrored plans are not visibly drifting.
- For delegated work, integrate results locally before presenting conclusions.
- Clean up temporary files, agents, claims, or scratch state that should not persist.

Final responses should follow the required Response Format and then remain concise and factual: state what changed/found, include proof, mention material risks/blockers, distinguish verified facts from hypotheses when relevant, and include a short orchestration ledger only when orchestration actually ran.

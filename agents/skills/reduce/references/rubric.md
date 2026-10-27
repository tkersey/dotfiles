# Reduce scoring rubric

Use this rubric for every abstraction candidate. Score from observed evidence; do not infer value from popularity, marketing purpose, or personal dislike.

## Columns

- `T`: agent/change tax, 0-3
- `V`: proven value, 0-3
- `D`: tax minus value, `T - V`
- `confidence`: high, medium, low
- `external obligation risk`: high, medium, low, unknown
- `essential abstraction`: product, coproduct, refined/equalizer, pullback, exponential, free, protocol, external obligation, none, unknown
- `verdict`: keep, wrap, slice, replace, delete

Keep `V` and external obligation risk separate. A layer can have low repo-proven value and high external risk.

## Tax score `T`

### `T = 0`: negligible tax

- The layer is local, explicit, and easy to bypass.
- A simple change usually touches one or two predictable files.
- Tests and runtime behavior are easy to trace.
- Proof latency is low.

### `T = 1`: mild tax

- The layer adds some ceremony or naming indirection.
- Local changes require looking at a few conventions or config files.
- Debugging remains straightforward.
- Diff opacity is low.

### `T = 2`: material tax

- The layer hides control flow, uses codegen/reflection/plugins, or spreads simple behavior across many files.
- Agent edits require understanding conventions, lifecycle, registration order, generated artifacts, or tool-specific side effects.
- Tests or local reproduction require non-obvious setup.
- Edit hops, lookup hops, or tool hops are high for simple changes.

### `T = 3`: severe tax

- The layer dominates change latency.
- Small behavior changes require touching many files, running generators, syncing schemas, updating multiple configs, or navigating hidden runtime wiring.
- Mistakes are easy to make and hard to detect locally.
- The layer blocks incremental agent editing or makes diffs opaque.
- Deployment/build weight is disproportionate to behavior.

## Value score `V`

### `V = 0`: no local proof of value

- No observed call sites, tests, docs, contracts, or runtime path require the layer.
- The layer appears unused, redundant, speculative, or cargo-culted.

### `V = 1`: weak or narrow value

- The layer supports a small amount of behavior, but most of its surface is unused.
- Benefits are plausible but not proven by tests, docs, production paths, or operational config.
- A smaller primitive would likely preserve behavior.

### `V = 2`: proven value

- The layer clearly provides useful behavior such as validation, transactionality, auth boundaries, schema compatibility, migrations, retries, caching, observability, routing, accessibility, or operational policy.
- Some tax remains, but the value is visible in real paths.

### `V = 3`: essential value

- The layer encodes behavior that is safety-critical, externally committed, security-sensitive, compliance-relevant, or operationally required.
- Removal would likely break public contracts, SLOs, data integrity, auditability, migration safety, or platform requirements.

## Interpreting `D = T - V`

- `D <= -1`: keep unless there is a narrow slicing opportunity.
- `D = 0`: keep or wrap; cut only if there is a no-risk simplification.
- `D = 1`: candidate for wrap, slice, or replace after proof.
- `D = 2`: strong candidate for replace or delete, subject to confidence and obligation risk.
- `D = 3`: urgent candidate for delete/replace if evidence confidence is high, external risk is low, and essential abstraction check is clear.

`D` is not a command. It is a priority signal. Confidence, external risk, and essential truth can lower the verdict.

## Confidence

### `high`

- You traced at least one real path.
- You found tests, scripts, docs, or config proving behavior.
- You checked imports/call sites or runtime registration.
- You know what rollback would be.
- The essential-abstraction check has an answer.

### `medium`

- You found meaningful code/config evidence but did not fully trace runtime behavior.
- You can suggest wrap/slice safely, but replace/delete needs more proof.
- Some external or protocol risk remains.

### `low`

- Evidence is mostly structural or based on filenames/patterns.
- Do not recommend destructive cuts.
- Cap at keep/wrap/slice.

## External obligation risk

### `high`

- Public API, compliance, security, audit, billing, data integrity, SLO, platform policy, migration safety, or customer contract may depend on the layer.
- Use keep, wrap, or slice unless explicit approval and proof exist.

### `medium`

- The layer touches external behavior, but the contract appears narrow or compatibility wrappers are feasible.
- Prefer wrap/slice before replace.

### `low`

- The layer is internal, locally testable, and rollback is simple.
- Replace/delete can be considered if confidence is high and essential truth is preserved.

### `unknown`

- The repo does not reveal obligations.
- Mark the audit provisional and avoid delete/replace until the unknown is resolved.

## Essential abstraction check impact

- `none`: normal verdict rules apply.
- `unknown`: cap destructive verdicts at wrap/slice.
- `product/coproduct/refined/pullback/exponential/free/protocol`: prefer split, wrap, or handoff to `universalist` unless the replacement explicitly preserves the truth.
- `external obligation`: prefer compatibility wrapper, contract-first replacement, or hold.

## Verdict rules

Use these defaults unless repo evidence justifies a different choice.

- `keep`: `V >= T`, confidence is low, external risk is high, or essential truth cannot yet be preserved.
- `wrap`: behavior is needed but callers should stop depending on the layer directly.
- `slice`: useful subset exists but unused surface/config/plugins/generated behavior can be removed.
- `replace`: `D >= 1`, confidence is medium/high, external risk is low/medium, and a lower-level primitive preserves behavior and essential truth.
- `delete`: `D >= 2`, confidence is high, external risk is low, usage is absent/redundant, tests or static analysis support removal, rollback is trivial, and essential abstraction check is `none` or explicitly preserved elsewhere.

## Minimum proof for replace/delete

Before `replace`:

- Identify equivalent lower-level primitive.
- Identify compatibility surface.
- Run or state at least one proof command or test.
- State rollback.
- State what behavior may change.
- State essential truth preservation.

Before `delete`:

- Show absence or redundancy of usage.
- Check static call sites/imports/config registration.
- Check tests/docs/runtime entrypoints where feasible.
- Verify no generated/deploy/CI path still depends on it.
- Provide rollback path.
- Verify no essential truth or external obligation is being silently removed.

## Common false positives

Do not score a layer as useless only because it looks abstract. Check whether it provides:

- transaction boundaries;
- idempotency;
- authorization or policy enforcement;
- compatibility with external schemas;
- retry/backoff/circuit-breaking;
- validation and sanitization;
- data migrations;
- observability and audit trails;
- multi-tenant isolation;
- state transitions or lifecycle constraints;
- accessibility or browser compatibility infrastructure;
- operational rollout/rollback controls.

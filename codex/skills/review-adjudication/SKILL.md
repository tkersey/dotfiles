---
name: review-adjudication
description: "Adjudicate PR review comments, CAS findings, and review-like claims before implementation or thread resolution. Emit Claim Decision Kernel rows and Resolution Warrants for address, validate, proof-only, do-not-address, delete/collapse/canonicalize, or blocked routes; mutation requires an active surface-budgeted warrant. Trigger for `$review-adjudication`, review the review, selecting review comments to resolve, gating comments before implementation, or routing review/CAS findings into `$fixed-point-driver`. Not for implementing fixes, rebuttals only, or final merge closure."
---

# Review Adjudication

## Intent

Decide what a review/CAS/comment claim may do downstream. A claim may be
unsupported, stale, proof-only, validation-only, implementation-worthy,
delete/collapse/canonicalize-worthy, or blocked. The output is not a narrative
recommendation; it is a compact permission boundary.

The invariant is simple:

> No downstream mutation, validation-only probe, thread resolution, rebuttal,
> defer handoff, or fixed-point implementation route is licensed unless a
> matching active Resolution Warrant exists.

## Default mode

Use **Kernelized Surface-Budgeted v9** for real review/CAS/comment sets.

Always emit the small mandatory kernel. Emit heavier annexes only when triggered.
This replaces the earlier monolithic full-report habit with a layered protocol:

1. **Claim Decision Kernel**: one stable row per raw claim. Always required.
2. **Resolution Warrants**: scoped, expiring permissions. Always required for
   every non-synthetic route, including no-change and blocked routes.
3. **Triggered annexes**: adversarial, ablative, isomorphic, clone, abstraction,
   and surface-budget detail only when the selected route can mutate, delete,
   collapse, canonicalize, or materially affect closure.
4. **Tail license summary**: the final visible handoff must show what is actually
   licensed and what is not.

Other modes may compress prose, but they must still emit the Claim Decision
Kernel, matching Resolution Warrants, the Adjudication Gate, Handoff Agenda, and
Adjudication Bottom Line.

## Doctrine

Operate in **DISCRIMINATIVE**, **REBUTTAL-FIRST**, **KERNEL-FIRST**,
**WARRANT-ISSUING**, **SURFACE-BUDGETED**, **ABLATIVE**, **ISOMORPHIC**,
**CLONE-CLASSIFIED**, **ABSTRACTION-LADDERED**, **CANONICALIZING**,
**EVIDENCE-WEIGHTED**, **STALE-PROOF**, and **FAIL-CLOSED** mode.

- **DISCRIMINATIVE**: a reviewer comment is a claim, not an obligation.
- **REBUTTAL-FIRST**: construct the strongest no-change or alternative-route
  countercase before selecting a downstream route.
- **KERNEL-FIRST**: every adjudication produces a compact row-level decision
  artifact even when the full annex set would be too heavy.
- **WARRANT-ISSUING**: downstream action is authorized by scoped warrants, not by
  prose, enthusiasm, or a broad “worth resolving” statement.
- **SURFACE-BUDGETED**: code mutation is licensed only under a measurable surface
  budget. Additive code is an exception, not the default.
- **ABLATIVE**: prefer deletion, reuse, collapse, privatization,
  decommissioning, canonicalization, or refactor before additive mutation.
- **ISOMORPHIC**: deletion/collapse/canonicalization requires behavior
  preservation proof or a validate-first route.
- **CLONE-CLASSIFIED**: apparent duplication must be classified before merging or
  abstracting it.
- **ABSTRACTION-LADDERED**: new helpers/adapters/interfaces/generics/flags must
  justify the abstraction rung and proof burden.
- **EVIDENCE-WEIGHTED**: current artifacts outrank memory; direct proof outranks
  reviewer intuition.
- **STALE-PROOF**: bind decisions and warrants to branch/head/base/diff/comment
  state so downstream skills can detect stale permissions.
- **FAIL-CLOSED**: missing identity, stale state, incomplete warrants, unchecked
  surface growth, or unresolved adversarial clearance blocks mutation.

## Contract

- Preserve raw claim identity. Do not replace ids, reviewers, locations, or exact
  excerpts with summaries.
- Preserve artifact-state identity. A warrant expires when the artifact state,
  claim set, or proof ref changes materially.
- Separate concern validity from proposed-fix validity.
- Separate adjudication route from permitted downstream action.
- `address` does not mean “add code.” It means a claim is eligible for a
  mutation-capable warrant under a surface budget.
- `delete-collapse-canonicalize` is a first-class route, not an implementation
  afterthought.
- `validate-only` permits proof/probe work, not production mutation.
- `resolve-thread-only` permits proof-bearing thread closure, not code changes.
- `do-not-address` preserves a no-change/defer/rebut route.
- `blocked` permits no downstream action except gathering missing evidence or
  asking the user.
- `$fixed-point-driver` may implement only from active `mutate-code` or
  `delete-collapse-canonicalize` warrants and must consume the surface budget.

## Required input context

When possible, build this compact context pack before adjudication:

```md
Review/CAS/comment claims:
- raw id/thread/finding id:
- source/reviewer:
- file/location:
- exact excerpt:
- suggested fix, if any:

Current artifacts:
- artifact_state_id:
  - branch:
  - base:
  - head:
  - diff_digest:
  - claim_set_digest:
  - ci_state:
- branch/diff summary:
- touched files:
- relevant tests / CI / local proof:
- PR description or stated goal:

Constraints:
- intended change:
- explicit non-goals:
- compatibility posture:
- ownership boundaries:
- proof bar:
```

Use `$seq` for rationale recovery only when PR intent is missing, disputed,
stale, or likely to change disposition. Do not use memory to manufacture
obligations.

## Claim Decision Kernel

Always emit this section for real claim sets, even in Fast or root-equivalent
mode.

```md
## Claim Decision Kernel

| id/thread | claim | current-state truth | route | warrant id | proof ref | status |
|---|---|---|---|---|---|---|
```

Allowed `route` values:

- `address`
- `validate-only`
- `resolve-thread-only`
- `do-not-address`
- `delete-collapse-canonicalize`
- `blocked`

Allowed `status` values:

- `licensed`
- `validation-needed`
- `proof-only`
- `no-change`
- `delete-collapse-canonicalize`
- `blocked`

Kernel rules:

- Every raw claim appears exactly once.
- Every row has a warrant id. Blocked and no-change decisions still require
  warrants so downstream tools know what is not licensed.
- `address` and `delete-collapse-canonicalize` require current artifact proof.
- `validate-only` requires a proof target and must not authorize production
  mutation.
- `resolve-thread-only` requires proof that mutation is unnecessary.
- `do-not-address` requires a preserved no-change/defer/rebut countercase.

## Resolution Warrants

Resolution Warrants are scoped, expiring permissions. They are the authority
object that downstream skills consume.

```md
## Resolution Warrants

| warrant id | claim id | source | selected route | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|
```

Allowed `permitted action` values:

- `mutate-code`
- `add-validation-only`
- `resolve-thread`
- `draft-reply`
- `defer`
- `none`

Route-to-action mapping:

- `address` -> `mutate-code`
- `delete-collapse-canonicalize` -> `mutate-code`
- `validate-only` -> `add-validation-only`
- `resolve-thread-only` -> `resolve-thread`
- `do-not-address` -> `draft-reply`, `defer`, or `none`
- `blocked` -> `none`

Every warrant must include:

- exact claim id
- selected route
- permitted action
- narrow permitted scope
- explicit forbidden actions
- concrete evidence refs or explicit missing evidence for blocked rows
- countercase ref
- proof required, unless action is `none`
- expiry condition mentioning artifact/head/base/diff/comment/claim/thread state

## Triggered annex rules

Do not make every adjudication emit every annex. Emit annexes when triggered.

### Address / mutation-capable routes

For `address` or `delete-collapse-canonicalize`, emit:

- `## Resolve Countercases`
- `## Adversarial Action Matrix`
- `## Ablative Counterproposal Ledger`
- `## Surface Budget Ledger`
- `## Warrant / Budget Summary`

### Delete / collapse / canonicalize routes

For `delete-collapse-canonicalize`, also emit:

- `## Ablative Isomorphism Cards`

### New abstraction / clone / helper / flag routes

When a selected route could introduce or merge helpers, adapters, interfaces,
base classes, generics, macros, flags, state variants, public symbols, wrappers,
or clone abstractions, the annex rows must include clone classification and
abstraction-ladder status.

### Root-equivalent shortcuts

Root-equivalent adjudication is allowed only when it emits the Claim Decision
Kernel and warrants. If a mutation-capable route is selected and the annexes are
not emitted, set `implementation_handoff_allowed: no`.

## Resolve Countercases

For every non-blocked route, challenge the selected route rather than merely the
concern.

```md
## Resolve Countercases

| id/thread | selected route | strongest alternative route | countercase status | evidence ref | route impact |
|---|---|---|---|---|---|
```

Allowed `countercase status` values:

- `defeated`
- `preserved-no-change`
- `preserved-validate-first`
- `preserved-proof-only`
- `preserved-ablative`
- `unresolved`
- `blocked`

## Adversarial Action Matrix

Every selected downstream action must be challenged before it is licensed.

```md
## Adversarial Action Matrix

| id/thread | selected route | adversarial challenge | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|
```

Allowed `veto status` values:

- `cleared`
- `preserved-no-change`
- `preserved-validate-first`
- `vetoed`
- `unresolved`
- `blocked`

Allowed `clearance` values:

- `cleared`
- `preserved`
- `rerouted`
- `downgraded`
- `blocked`

## Ablative Counterproposal Ledger

For every mutation-capable route, prove that lower-surface options were selected
or defeated before licensing additive work.

```md
## Ablative Counterproposal Ledger

| id/thread | additive proposal | delete candidate | collapse/reuse candidate | canonical owner candidate | privatization/decommission candidate | clone classification | abstraction-ladder check | lower-surface route | why insufficient or selected | ablative clearance | proof ref |
|---|---|---|---|---|---|---|---|---|---|---|---|
```

Allowed `lower-surface route` values:

- `delete`
- `collapse`
- `reuse`
- `canonicalize`
- `privatize`
- `decommission`
- `refactor-existing-seam`
- `validate-first`
- `proof-only`
- `none`

Allowed `ablative clearance` values:

- `select-ablative-route`
- `clear-additive`
- `validate-first`
- `veto-additive`
- `unresolved`
- `not-required`

## Ablative Isomorphism Cards

For deletion, collapse, merge, reuse, or canonicalization, prove behavior
preservation or route to validation-first.

```md
## Ablative Isomorphism Cards

| id/thread | surface | proposed action | behavior preserved | public contract preserved | error/order/side effects preserved | compatibility risk | proof signal | card status |
|---|---|---|---|---|---|---|---|---|
```

Allowed `card status` values:

- `pass`
- `validate-first`
- `missing`
- `not-required`

## Surface Budget Ledger

Every `mutate-code` warrant must carry a surface budget.

```md
## Surface Budget Ledger

| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | subtractive probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

Allowed `mode` values:

- `ablative-first`
- `additive-authorized`
- `proof-only`
- `validation-only`
- `not-applicable`

Default for `mutate-code` is `ablative-first`. `additive-authorized` is legal
only when deletion, reuse, collapse, canonicalization, privatization,
decommissioning, and refactor probes are defeated with current evidence.

Allowed `target net loc` values:

- `negative`
- `zero`
- `small-positive`
- `unknown`
- `not-applicable`

## Fixed-point-driver surface handshake

`$review-adjudication` issues budgets; `$fixed-point-driver` consumes them.
When any implementation route goes to `$fixed-point-driver`, the handoff must
request these downstream receipts:

```md
Surface Budget Preflight:
- warrant id:
- feature to preserve:
- deletion / reuse / collapse / canonicalization / refactor probes:
- selected first implementation shape:
- budget status before patch:

Surface Delta Receipt:
- warrant id:
- patch group:
- files changed:
- insertions/deletions/net:
- public symbols/helpers/flags/state/branches added:
- deleted/collapsed paths:
- budget status:

Expansion Warrant Request:
- only if the patch must exceed budget
- additive surface requested:
- defeated lower-surface route refs:
- proof that added surface reduces total semantic surface:

Surface Budget Closure:
- final diff within budget: yes/no
- proof passed:
- unresolved expansion debt:
```

## Warrant / Budget Summary

Before the final handoff, emit a compact visible license summary:

```md
## Warrant / Budget Summary

| warrant id | claim id | route | permitted action | surface budget status | ablation status | implementation allowed |
|---|---|---|---|---|---|---|
```

This section is mandatory when any route is `address` or
`delete-collapse-canonicalize`.

## Adjudication Gate

Before handoff, emit:

```md
## Adjudication Gate

| field | value | basis |
|---|---|---|
| claim_kernel_complete | pass/fail |  |
| artifact_state_bound | pass/fail |  |
| warrant_coverage | pass/fail |  |
| route_annexes_complete | pass/fail/not-required |  |
| surface_budget_coverage | pass/fail/not-applicable |  |
| fixed_point_handoff_complete | pass/fail/not-applicable |  |
| handoff_agenda_consistency | pass/fail |  |
| adjudication_complete | pass/fail |  |
| implementation_handoff_allowed | yes/no |  |
| validation_handoff_allowed | yes/no |  |
| reply_handoff_allowed | yes/no |  |
```

`adjudication_complete` may be `pass` only when all required fields pass, except
fields explicitly marked `not-required` or `not-applicable` by route.

If any required field fails, the bottom line must say:

```md
Blocked: incomplete adjudication. Do not implement yet.
```

## Handoff Agenda

Use explicit ids. Never use `all`.

```md
## Handoff Agenda

- implementation items:
- delete/collapse/canonicalize items:
- validation-only items:
- proof-only thread-resolution items:
- reply/defer/no-change items:
- blocked items:
- fixed-point-driver surface handshake required: yes/no/not-applicable
- proof:
```

## Tail output contract

End with these sections, in order:

1. `Act On`
2. `Validate Only`
3. `Delete / Collapse / Canonicalize`
4. `Rebut / Do Not Address`
5. `Need Evidence / Blocked`
6. `Warrant / Budget Summary`
7. `Handoff Agenda`
8. `Adjudication Bottom Line`

`Adjudication Bottom Line` must be the final section and must name the single
next action.

## Machine-check hook

When automation is available, run:

```bash
python codex/skills/review-adjudication/tools/review_adjudication_gate.py adjudication.md
```

For post-implementation budget checking:

```bash
python codex/skills/review-adjudication/tools/review_adjudication_gate.py adjudication.md \
  --changed-files src/foo.zig,test/foo_test.zig \
  --diffstat "2 files changed, 12 insertions(+), 30 deletions(-)"
```

## Hard rules

- Never issue implementation permission without an active warrant.
- Never let `address` authorize unbounded additive implementation.
- Never route `validate-only`, `resolve-thread-only`, `do-not-address`, or
  `blocked` to production mutation.
- Never emit `delete-collapse-canonicalize` without either an Ablative
  Isomorphism Card or a validate-first route.
- Never let `$fixed-point-driver` implement beyond the warrant scope or surface
  budget without an Expansion Warrant Request.
- Never use reviewer authority as evidence.
- Never hide identity, uncertainty, or stale artifact state.

## Resources

- [schema-v9.yaml](references/schema-v9.yaml)
- [claim-decision-kernel.md](references/claim-decision-kernel.md)
- [surface-budget-warrants.md](references/surface-budget-warrants.md)
- [fixed-point-driver-surface-handshake.md](references/fixed-point-driver-surface-handshake.md)
- [adjudication-output-template.md](references/adjudication-output-template.md)
- [adjudication-gate-contract.md](references/adjudication-gate-contract.md)
- [ablative-clearance.md](references/ablative-clearance.md)
- [example-invocations.md](references/example-invocations.md)

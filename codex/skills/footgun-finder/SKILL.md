---
name: footgun-finder
description: "Read-only review lens for latent misuse hazards: APIs, defaults, flags, fallbacks, examples, config, state, cleanup, permissions, and workflows where the easy or obvious use is unsafe, surprising, irreversible, or likely to be copied wrong. Use for `$footgun-finder`, footguns, sharp edges, dangerous affordances, trap doors, misleading names, unsafe defaults, partial-success ambiguity, hidden coupling, or review requests focused on future misuse. Not for generic bugs, invariant ownership, or local simplification unless the hazard is a misuse trap."
---

# Footgun Finder

## Mission

Find code and interface shapes where a reasonable future caller, maintainer, user,
or reviewer can do the wrong thing easily and believe they did the right thing.

```text
available affordance
+ plausible user/caller belief
+ surprising or dangerous consequence
= footgun candidate
```

This skill is a **read-only review lens**. It does not implement fixes, resolve
comments, create tickets, or certify closeout. It produces a ranked footgun
ledger, mitigation candidates, and handoff routes.

## Definition

A footgun is not merely a bug. A footgun is a design or implementation surface
that makes misuse likely:

```text
wrong path is easy
right path is non-obvious
failure is silent, late, misleading, or expensive
copy/paste or default use preserves the trap
```

Footguns may already be bug-causing, but they are especially important when the
current code passes tests while future use remains hazardous.

## Boundary with companion skills

Use this skill with, but do not replace:

- `$invariant-ace` when the hazard is an illegal state that needs an owned
  inductive invariant, counterexample trace, enforcement boundary, or witness
  parity gate.
- `$complexity-mitigator` when the hazard is primarily local comprehension cost,
  dominated branches, duplicated factors, or incidental complexity.
- `$review-adjudication` when the input is a reviewer claim that must be
  classified before mutation.
- The owning implementation workflow only after this review emits a concrete
  mitigation handoff.

If a finding is both a footgun and an invariant failure, classify the footgun
surface here, then hand off the invariant proof to `$invariant-ace`.

If a finding is both a footgun and inessential complexity, classify the trap
here, then hand the clarity cut to `$complexity-mitigator`.

## Use when

- APIs, CLIs, config, examples, docs, defaults, flags, fallbacks, retries,
  cleanup, auth, permissions, persistence, or state machines seem easy to use
  incorrectly.
- Review asks for sharp edges, dangerous defaults, future misuse, trap doors,
  hidden coupling, gotchas, unsafe examples, or accidental privilege.
- A change looks technically correct but may create a misleading affordance.
- A successful path and a degraded path are too easy to confuse.
- A partial-success or fallback path looks like success to the caller.
- Tests prove current behavior but do not protect plausible misuse.

Do not use for generic style review, broad architecture essays, pure performance
work, or bugs with no plausible misuse surface.

## Footgun taxonomy

Classify each candidate with one primary type:

```text
unsafe_default
  default behavior is riskier than a reasonable caller expects

misleading_name_or_shape
  name, return value, type, path, example, or docs imply stronger safety than exists

silent_degradation
  fallback, partial result, cache hit, retry, or degraded mode looks like normal success

ambiguous_authority
  call site can bypass policy, ownership, permission, review, or source-of-truth boundary

irreversible_or_expensive_easy_path
  destructive, external, persistent, billing, network, or migration side effect is too easy

copy_paste_trap
  example, fixture, README, test, or generated snippet encourages unsafe real use

state_or_lifecycle_trap
  operation depends on ordering, freshness, cleanup, lease, lock, epoch, or handle validity

validation_gap
  accepted input or config shape looks valid but later fails in a surprising place

observability_gap
  failure gives no stable explanation, next legal action, or proof of what happened

concurrency_or_idempotency_trap
  retries, duplicates, races, stale handles, or parallel calls appear safe but are not

security_or_privacy_trap
  token, path, command, host, permission, user data, or capability boundary is easy to leak or bypass

compatibility_trap
  version, platform, feature flag, migration, schema, or protocol difference is hidden until runtime
```

## Severity model

Rank by expected harm and likelihood, not by how annoying the code looks.

```text
P0  likely data loss, security/privacy exposure, irreversible destructive action,
    production outage, or policy bypass from plausible normal use
P1  high-probability misuse causing wrong behavior, false proof, lost work,
    persistent state corruption, or expensive recovery
P2  plausible misuse with bounded impact, confusing degraded behavior, or costly debugging
P3  minor sharp edge, confusing naming, or low-likelihood trap with easy recovery
```

A low-LOC issue can be P0. A large messy module can be no footgun if misuse is
not plausible.

## Review workflow

### 1. Establish the reviewed surface

Record:

```text
artifact state:
  repo/ref/head or supplied file version
surface:
  API | CLI | config | docs/example | workflow | state machine | policy boundary | test fixture | internal helper
principal user/caller:
  end user | maintainer | integrator | future implementer | test author | automation
```

Name the expected reasonable belief for that principal.

### 2. Scan for affordance traps

Ask:

- What is the easiest call, flag, default, example, or copied pattern?
- What would a reasonable user infer from the name or docs?
- What hidden precondition, freshness rule, authority boundary, cleanup, or
  version assumption must be true?
- Does degraded or partial success look like success?
- Is the dangerous path easier than the safe path?
- Does a test or example teach an unsafe real-world pattern?
- What happens if this is retried, run twice, interrupted, or copied to another
  context?

### 3. Require a misuse trace

Every material footgun needs a concrete misuse trace:

```text
actor -> action -> reasonable belief -> hidden fact -> consequence -> why current surface permits it
```

If no plausible actor and action exist, classify as `not_a_footgun` even if the
code looks odd.

### 4. Separate hazard class from remedy class

For each accepted footgun, choose the smallest truthful mitigation class:

```text
make_safe_default
require_explicit_opt_in
rename_or_retype
split_safe_and_dangerous_paths
fail_closed_or_block
surface_degraded_state
bind_to_owner_or_policy
validate_at_boundary
add_idempotency_or_freshness_guard
add_dry_run_or_preview
repair_example_or_docs
add_diagnostic_or_next_action
handoff_to_invariant_ace
handoff_to_complexity_mitigator
no_change
```

Do not jump from hazard to implementation. The output is a mitigation agenda, not
a patch.

### 5. Check companion-lens overlap

Before final ranking, classify whether each candidate is primarily:

```text
footgun
invariant
complexity
review_claim
ordinary_bug
non_issue
```

A footgun can overlap, but one lens should own the next step.

## Footgun ledger

Use this row shape:

| id | priority | type | surface | actor | easy path | reasonable belief | hidden hazard | consequence | evidence | mitigation | owner/handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|

Rules:

- Use stable IDs: `FG-001`, `FG-002`, ...
- Evidence should cite the smallest path, symbol, command, example, config key,
  or test scope available.
- Each accepted row must include both the easy path and the hidden hazard.
- Do not mark something P1/P0 without a plausible normal-use trace.

## Output modes

### Compact review

Use for one file, one API, one review comment, or quick preflight:

```text
Footgun Review:
- surface:
- accepted footguns:
- top hazard:
- not footguns:
- handoffs:
- bottom line:
```

### Full review

Use for broad review or when several surfaces interact:

1. `Review Basis`
2. `Surface Map`
3. `Footgun Ledger`
4. `Misuse Traces`
5. `Rejected / Downgraded Candidates`
6. `Companion-Lens Handoffs`
7. `Mitigation Agenda`
8. `Proof / Validation Signals`
9. `Footgun Bottom Line`

### Review companion mode

When used alongside `$invariant-ace` and `$complexity-mitigator`, output only:

```text
Footgun Lens:
- P0/P1 hazards:
- easy path -> hidden hazard traces:
- overlap with invariant/complexity:
- mitigation handoff:
```

## Mitigation agenda

The agenda must be an exact projection of accepted ledger rows:

| id | mitigation class | proposed change shape | proof signal | handoff owner |
|---|---|---|---|---|

Good proof signals include:

- misuse test that now fails closed;
- example updated so unsafe pattern is no longer copyable;
- degraded state visible in structured output;
- dangerous path requires explicit opt-in;
- fallback result is distinguishable from primary success;
- stale/duplicate/partial state is blocked before side effects;
- policy owner validates or denies the exception.

## Guardrails

- Do not implement.
- Do not inflate every bug into a footgun.
- Do not demand maximal safety when the hazard is low-impact and well signposted.
- Do not hide behind documentation if the surface can cheaply prevent misuse.
- Do not add ceremony when a rename, explicit flag, type split, or fail-closed check
  would remove the trap.
- Do not use broad words like `unsafe` without a misuse trace.
- Do not count merely surprising implementation internals unless a caller can
  reasonably touch or copy the hazard.

## Final report

End with:

```text
Footgun Bottom Line:
- highest-risk footgun:
- easiest wrong path:
- smallest mitigation:
- companion handoff:
- proof signal:
```

## Hard rules

- The easy path must be named.
- The reasonable belief must be named.
- The hidden hazard must be named.
- The consequence must be plausible.
- The mitigation must reduce misuse likelihood, not merely explain the code.
- If the right fix is an owned invariant, hand off to `$invariant-ace`.
- If the right fix is local winnowing, hand off to `$complexity-mitigator`.
- If the right fix is review-claim adjudication, hand off to `$review-adjudication`.

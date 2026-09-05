# Human Execution Specification

The ordinary public plan is the primary semantic representation, not a lossy summary
of an internal EPG. It remains self-contained whether or not a machine export exists.

## Completeness

Given the target repository, a fresh implementation session must be able to choose,
order, realize, validate, roll back, and determine completion using only the emitted
`<proposed_plan>` block. Do not depend on the original candidate, conversation,
private synthesis, inaccessible attachments, or an omitted machine representation.

Compression may remove duplicates, empty sections, schema syntax, and bookkeeping;
it must preserve required behavior, constraints, compatibility, material design
choices, branches, actions, proofs, abort criteria, and terminal predicates. An
unresolved material choice needs an exact observation-conditioned envelope or blocks.

## Shape

Emit one block, using these headings where applicable:

```text
Summary
Governed Specification
Architecture Decisions
Implementation Sequence
Decision Points and Branches
Proof, Rollback, and Done-State
Plan Identity and Source
```

The summary identifies the objective, chosen path, first action, and binary done-
state. The governed specification preserves current state, scope, non-goals, user-
fixed decisions, selected defaults, behavior, compatibility, and proof authority.
Do not label a planner's default a locked user decision.

Architecture decisions identify the consequential owner and boundary, authority
class, incumbent-to-target change, law, falsifier, factor dispositions, and invalidators.
Say which mechanisms are revisable means. Accepting a plan does not turn all its
means into hard requirements. No architecture section is needed for unchanged,
owner-local work with no live semantic boundary decision.

The implementation sequence is dependency-ordered. Each consequential action names
its stable ID and outcome, exact paths/symbols, prerequisite actions and evidence,
intended change, invariants, proof command or exact verifier reference, and failure
or rollback route. Broad verbs such as "update relevant files" are not executable
instructions. Migration and retirement belong with the mechanisms they replace.

Decision points use `unknown -> exact observation -> outcome-conditioned route`.
Include unavailable, invalid, or inconclusive evidence when material. Say what may
proceed before the observation and what must wait. An empirical choice may remain
conditional; a hidden user judgment may not be disguised as an experiment.

Proof binds the supported invalid family and preserved valid domain to the actual
enforcement mechanism, coverage source, discriminator, and claim strength. Proof
must belong to the branch that can produce it: evidence from an unselected branch
cannot close an obligation. State exact commands, artifact binding, abort criteria,
restoration proof, and the binary completion predicate. A proposed proof is not an
executed proof or a universal theorem.

Identity names the plan ID, revision, target repository/branch and inspected state,
source authority and decisions, material invalidators, and persistence status/path.
Hash only bytes actually available and computed. No EPG or Ledger digest is required
for human-only output. Do not put an export digest inside the primary block: the
optional export embeds this block and cannot hash itself.

## Final check

Perform the final reread defined in policy-synthesis-fixed-point.md on the exact
block, not a richer private draft. Ask whether an unfamiliar implementation owner
could proceed without inventing requirements, design choices, proof commands, or
failure routes. Walk each live branch through completion or an explicit safe stop.
Return missing semantics to synthesis, without an extra audit artifact.

For `human` and `both`, report `Plan synthesized.` only when complete. For machine
views, follow epg-export.md. A human-only plan must never claim EPG validation.

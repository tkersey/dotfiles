# Recall Workflow

## Recall Workflow

```bash
ledger project \
  --definition "$learnings_definition" \
  --projection recall \
  --repo "<repo-root>" \
  --param "query=<focused component failure objective terms>" \
  --param "now=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --param search_limit=5 \
  --param drop_superseded=true \
  --format json
```

Do not use `recall` as a substitute for current artifact inspection. Recall
returns candidates, not instructions: its compact result omits evidence and
full context.

## Before consequential use

Before a recalled learning materially changes the approach, inspect its complete
canonical record, not just its score or summary:

```bash
ledger project \
  --definition "$learnings_definition" \
  --projection record \
  --repo "<repo-root>" \
  --param id=lrn-... \
  --format json
```

Check the evidence, application conditions, and material uncertainty against the
current artifact. Expand only candidates that could change the decision, not
every search hit. Reuse an already inspected unchanged record within the task;
recheck when the source or relevant artifact facts change. Missing evidence is
not permission to reconstruct a canonical record from memory or assume it applies.

Apply the supported rule, use only a justified narrower interpretation, or leave
it unapplied. An inapplicable learning does not prohibit the route. If current
witnessed evidence corrects the learning, evaluate the existing capture gate and
supersession workflow. Keep routine use-time judgments internal; do not generate
a receipt or append merely because a learning was recalled.

## Co-application

When recalled rules materially shape the same decision and share state,
ownership, ordering, or applicability assumptions, check their conjunction.
Individually passing cases do not establish compatible composition. For example,
parse-result reuse and request isolation need to agree on whether the reused
object is immutable, copied, or shared and mutable.

Resolve a missing precondition from inspectable evidence, or use a targeted
interaction check when authorized and necessary. Its oracle must come from the
independent task requirement, not either rule's wording. Do not call a suspected
conflict witnessed without evidence; retain uncertainty or leave the unsupported
combination unapplied. Narrow or supersede misleading guidance rather than
accumulating exceptions. Do not scan all pairs, introduce fixed challenge rounds,
or invoke another source solely to perform this check.

A learning cannot override an active exact applicable Negative Ledger exclusion.
When a proposed route resembles a witnessed prior failure, use that source's
canonical route gate and existing lifecycle; a positive learning is not a vote
to bypass it. Otherwise recall alone does not activate Negative Ledger.

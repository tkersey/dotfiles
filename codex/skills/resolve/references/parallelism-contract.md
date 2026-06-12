# Resolve Parallelism Contract

Parallelism is allowed only when it reduces wall time without increasing state ambiguity.

## Root owns

The root `$resolve` process owns:

- clean-review streak;
- backend/base/head/fingerprint pins;
- CAS lane lifecycle;
- branch mutations;
- commits and pushes;
- PR-thread decisions;
- abstraction route selection;
- completion claims.

## Allowed sidecars

Allowed when tied to a named decision:

- repository/manifest/validation discovery;
- applicable language/tool skill discovery;
- CAS version/help checks;
- PR metadata/comment/thread fetching;
- CI/check discovery;
- review receipt summarization after root captures verdict;
- duplicate detection;
- stale-comment checks;
- read-only evidence gathering for adjudication;
- read-only evidence gathering for abstraction ladder rungs;
- safe validation-read-mostly commands when language/tool guidance permits.

## Forbidden sidecars

- mutating working tree/index/dependency state/lockfiles/generated artifacts;
- staging, committing, pushing, rebasing, amending, resolving threads, dismissing comments;
- choosing/changing review base;
- owning or incrementing clean-review streak;
- selecting final abstraction route without root acceptance;
- starting duplicate review attempts for same backend/base/head/fingerprint;
- running the three required clean reviews in parallel;
- declaring `$resolve` complete.

## Ledger entry

```yaml
parallel_task_ledger_entry:
  task_id:
  artifact_snapshot:
    base_ref:
    base_sha:
    head_sha:
    target_fingerprint:
  task_kind:
  side_effect_profile: read-only | validation-read-mostly
  named_decision:
  allowed_outputs: []
  started_at:
  completed_at:
  result_summary:
  used_for_state_transition: true|false
```

Sidecar results are advisory until joined and accepted by root against current pinned artifact state.

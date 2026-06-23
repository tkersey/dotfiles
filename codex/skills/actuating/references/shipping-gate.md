# Shipping Gate

`$ship` is allowed only when:

- current GCR and projection are valid;
- no unhandled in-scope tasks remain;
- every material AFR is terminal;
- no `return_to_frontier` observation remains unresolved;
- focused and wave proof is accounted for;
- full closure proof matches current head;
- no surface-budget or specialist blocker remains;
- PR publication is in scope;
- explicit PR mode exists.

Ready is the default after full validation.

## Handoff

```yaml
ship_handoff:
  target_skill: ship
  run_id:
  artifact_state:
    branch:
    base:
    head:
    dirty_fingerprint:
  graph:
    gcr_id:
    projection_valid:
    complete:
    blocked:
    deferred:
    open:
  frontier:
    afr_refs: []
    terminal:
    return_to_frontier:
    blocked:
    open:
  validation:
    focused: pass | fail | missing | stale
    wave: pass | fail | missing | stale
    closure: pass | fail | missing | stale
    closure_artifact_fingerprint:
  surface:
    helpers_added:
    branches_added:
    fields_added:
    public_symbols_added:
    fallback_paths_added:
    test_families_added:
    surfaces_retired: []
  pr_mode: ready | draft | update-existing | promote-draft | blocked
  pr_mode_reason:
  draft_allowed_reason:
  proof_summary:
  existing_pr:
    exists: yes | no | unknown
    url:
    draft: yes | no | unknown
```

`$ship` must honor `pr_mode` and must not create a draft when mode is `ready`.

`$ship` creates/updates/promotes a PR. It does not merge.

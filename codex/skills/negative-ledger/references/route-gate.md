# Negative Ledger route selection

Read [store.md](store.md) before the canonical projection. Entry-point authority,
valid-status and no-fallback rules remain binding.

## Route-Gate Workflow

For review-driven repair, apply the owner boundary in
[counterexample-construction-integration.md](counterexample-construction-integration.md).

1. Identify the resolved `repository_id`, immutable `artifact_state_id`, readable
   `artifact_state_label`, route, cluster, scope, target signal, and changed surface.
   For new captures, use the stable repository identity from Ledger context;
   branch/worktree paths are provenance. A commit alone does not identify relevant
   dirty code, fixtures, or configuration; use a supported immutable surface
   identity when those affect the claim.
2. Run:

   ```bash
   ledger project \
     --definition "$negative_ledger_definition" \
     --projection route-gate \
     --store-root "<context.store_root>" --store-id "<context.store_id>" \
     --param "artifact=<artifact-state-id>" \
     --param "identity=<declared-scope-identity>" \
     --format json
   ```

3. Interpret exit codes: `0` no active exact exclusion, `2` active exact/applicable
   exclusion, `3` canonical context/store unavailable or invalid. Never turn a
   failed managed lookup into an empty checkout-local gate.
4. Pass the identity for the declared exact, route, route-family, cluster,
   authority-model, distinction-pattern, or proof-pattern scope.
5. Treat fuzzy candidates as search hints only.
6. Recheck current applicability before suppression. A record inapplicable to
   this worktree does not, by itself, justify globally marking it stale/reopened
   for another artifact. Global lifecycle changes retain their proof obligations.
7. Resolve symbolic Git refs before the call. Pass immutable identity as
   `artifact`, retaining readable provenance in `artifact_state_label`.


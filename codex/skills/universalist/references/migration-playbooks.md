# Migration playbooks

## Adapter-first internal model

1. Keep external DTO/row/message shape stable.
2. Add boundary decoder into the stronger model.
3. Add internal constructor/eliminator.
4. Add parity tests.
5. Migrate one seam.

## Legacy-to-new projection

1. Add old-view adapter.
2. Run old golden tests through the adapter.
3. Move internals behind the new model.
4. Delete duplicate old projections only after tests pass.

## Explicit IR migration

1. Encode one callback/handler as a constructor.
2. Add interpreter equivalence test.
3. Move one call site.
4. Repeat only after the seam is verified.

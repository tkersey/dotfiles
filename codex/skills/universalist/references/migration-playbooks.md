# Migration playbooks

## Adapter-first staged migration

1. Add adapter/decoder at public boundary.
2. Introduce stronger internal model.
3. Add parity tests.
4. Route one seam through the model.
5. Stop and record next seam.

## Lift-shaped migration

1. Capture current or required public behavior as fixtures.
2. Define `P : internals -> observations`.
3. Realize one public case internally.
4. Assert `P(realizer) == required` or a sound/covering variant.
5. If no exact lift exists, report the missing evidence or structure.

## Freyd/AFT-style free-builder migration

1. Identify a bounded family of implementation templates.
2. Define a builder from required behavior to internal realizer.
3. Project the realizer back through `P`.
4. Add obstruction tests for lossy projections and unsupported templates.

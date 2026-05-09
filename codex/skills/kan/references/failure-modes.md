# Failure modes

- Decorative Kan language: no concrete `K`/`P`, witness, or law test.
- Wrong axis: using `Lan/Ran` when the unknown is behind a projection, or lift language when the problem is a pushforward.
- Wrong direction: left/right comparison cell reversed.
- Hidden projection: `P` is scattered across code and cannot be tested.
- No exact lift: desired behavior requires observations not stored, derivable, projected, or externally obtainable.
- False free builder: `Free` is ad hoc codegen with no projection law.
- Over-defunctionalization: replacing simple local functions with noisy enums.
- Under-defunctionalization: important boundary callbacks remain untestable and unserializable.

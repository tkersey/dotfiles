# Review Compression Boundary

When invoked from `$resolve` or `$fixed-point-driver` after review findings, do not accept raw `address` as mutation authority.

Require one of:

- accepted `review_compression_packet`;
- structured `not-required` packet proving isolated existing-owner direct proof;
- explicit user-scoped implementation outside review compression.

Preserve selected normal form, forbidden actions, surface budget, rent status, proof matrix, and stale conditions.

If implementation discovers the normal form is insufficient, stop and route back to `$review-compression-compiler` instead of adding local patches.

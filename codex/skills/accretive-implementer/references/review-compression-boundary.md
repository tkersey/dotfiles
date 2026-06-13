# Review Compression Boundary

When invoked from `$resolve` or `$fixed-point-driver` after review findings, do not accept a raw review comment or `address` route as mutation authority by itself.

Require one of:

- accepted `review_compression_packet`;
- structured not-required route receipt proving isolated existing-owner direct proof;
- explicit user request for a scoped implementation outside review compression.

If a `review_compression_packet` is present, implement only its selected normal form and preserve:

- permitted scope;
- forbidden actions;
- surface budget;
- abstraction rent status;
- proof matrix;
- stale conditions.

If implementation discovers the selected normal form is insufficient, stop and route back to `$review-compression-compiler` instead of adding local patches.

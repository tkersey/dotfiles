# Patch Notes

Version: `7.1.0`

Repairs the unrecorded refactor-kernel route observed by the 2026-07-05
fresh-eyes `$seq` audit.

Adds:

- `actuation_refactor_kernel_gate.py` with `check-decision`, `make-outcome`, and
  `check-outcome` commands.
- RKO-v1 `refactor_kernel_outcome` fixture and validator.
- Stronger AER-v1 example with multiple joinable accepted liabilities.
- Quick validation coverage for the refactor-kernel gate and tests.

Preserves:

- APMA-v1 pre-mutation authority.
- actuation-authority receipt self-invalidating stop rule.
- ADD-v1 post-integration delivery handoff.
- ATCG-v1 terminal completion guard.
- Standard-only CAS clean-run accounting.

Critical repair:

```text
broad owner-boundary implementation is not governed refactor-kernel by itself
refactor-kernel route -> AER-v1 decision gate before mutation
refactor-kernel result -> RKO-v1 outcome gate after proof/review
RKO-v1 governance.graph_bypass=yes -> gate failure
nonzero mutations_without_graph_control_receipt -> gate failure
```

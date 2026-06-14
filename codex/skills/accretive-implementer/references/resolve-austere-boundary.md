# Resolve Austere Boundary

When invoked from `$resolve` after review findings, do not accept raw `address` as mutation authority.

Require:

- selected route from `resolve_decision_record`;
- stop-rule status;
- negative route gate;
- permitted scope;
- forbidden actions;
- proof matrix;
- surface budget.

If the same cluster reappears or implementation exceeds the selected route, stop and route back to `$resolve` / `$negative-ledger`.

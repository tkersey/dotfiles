# Resolve Austere Handoff

When `$resolve` supplies a `resolve_decision_record`, implement the selected route, not the review comment queue.

Reject mutation when:

- same-cluster stop rule is open;
- selected route violates active negative evidence;
- proof matrix is missing;
- forbidden actions or scope are missing;
- route is `add-new-surface` without explicit expansion acceptance;
- route is just another point fix after same-cluster recurrence.

If the same cluster reappears after implementation, route back to `$resolve` stop rule and `$negative-ledger`.

# Review Route Ratchet

Before repeating a route in a hot cluster, check whether it was already falsified.

If an active exclusion matches the selected route, block unless the evidence is reopened, stale, superseded, or explicitly accepted as risk.

Same-cluster recurrence after a selected route creates a capture candidate.

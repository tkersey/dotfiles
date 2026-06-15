# Review Governor Record

The `review_governor_record` is the control state for a finding-bearing review wave.

It records:

- artifact state;
- sensor inputs;
- state estimate;
- candidate routes;
- negative memory;
- cybernetic context;
- selected route;
- implementation handoff;
- outcome metrics;
- gates.

A production mutation after same-cluster recurrence requires this record.

If the record cannot explain why the selected route reduces review entropy, do not mutate.

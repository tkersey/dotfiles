# Execution Policy Fresh-Eyes Pass

Reread the final EPG from the governed or direct source. Do not trust the synthesis
path that produced it.

Check:

- source digest, governed specification, and inspected artifact state agree;
- no semantic decision was smuggled into structural validation;
- regime classification fits actual causal uncertainty;
- every critical unknown has observable evidence or an explicit block/revision;
- each action has bounded effects, failure observations, proof, and rollback;
- policy rules reference only declared atoms and actions;
- every modeled action outcome reaches another rule or terminal state;
- safety rules cover irreversible and authority-sensitive actions;
- potential cannot reward metric gaming while violating the objective;
- commitment horizon remains evidence-responsive;
- success terminal proves the governed source contract;
- human projection and governed specification do not contradict EPG;
- `return_to_spec` routes to a future Plan revision's internal specification phase;
- exact-byte Ledger validation returns the expected definition ID, digest, ABI, and
  `valid: true`.

If a material issue remains, revise or restart the affected specification/policy
phase and rerun downstream synthesis. Otherwise emit the selected validated view:
human without inline EPG JSON, raw JSON without prose or Markdown delimiters, or both
with validation bound to the payload inside the fence. Do not create an audit
artifact or readiness gate.

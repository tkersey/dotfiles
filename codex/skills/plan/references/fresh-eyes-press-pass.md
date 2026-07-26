# Execution Policy Fresh-Eyes Pass

Reread the final EPG from source. Do not trust the synthesis path that produced it.

Check:

- source/spec digest and inspected artifact state match the state against which the
  EPG is being synthesized;
- no semantic decision was smuggled into policy compilation;
- regime classification fits the actual causal uncertainty;
- every critical unknown has observable evidence or an explicit block/return;
- each action has bounded effects, failure observations, proof, and rollback;
- policy rules reference only declared atoms and actions;
- every modeled action outcome reaches another rule or terminal state;
- safety rules cover irreversible and authority-sensitive actions;
- potential cannot reward gaming the metric while violating the goal;
- commitment horizon is short enough to remain evidence-responsive;
- success terminal proves the source contract;
- human projection does not contradict EPG;
- when a compatible compiler is available,
  `seq execution-policy-compile --file <epg.json> --format json` returns
  `compiled: true` for the exact emitted EPG and reports its structural contract.

If a material issue remains, revise or return it and restart the affected synthesis
lens. Otherwise emit the EPG whether or not optional compiler validation was
available. Do not create an audit artifact or readiness gate.

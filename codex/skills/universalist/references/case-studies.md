# Case studies

## Lifecycle matrix to coproduct

Signal: booleans and nullable fields encode one lifecycle.
Construction: coproduct.
Proof: invalid legacy fixture rejected and all cases handled.

## Rule syntax to free construction

Signal: rules mix execution, explanation, and logging.
Construction: explicit rule AST plus interpreters.
Proof: old execution and new interpreter match fixtures.

## Public contract to lifted implementation

Signal: contract tests define internals.
Construction: lifted implementation.
Proof: `project(realize(case)) == required(case)`.

## Lossy projection to Freyd/AFT obstruction

Signal: public behavior requires cancellation reason, but `P` projects an internal order without retaining reason.
Construction: obstruction report plus obligation IR.
Proof: fixture fails until the internal model stores or reconstructs reason.

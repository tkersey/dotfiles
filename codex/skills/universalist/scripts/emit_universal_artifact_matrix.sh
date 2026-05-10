#!/usr/bin/env bash
set -euo pipefail
cat <<'OUT'
| Smell | Canonical boundary artifact | Universal reading | First proof signal |
| --- | --- | --- | --- |
| Many consumers interpret commands differently | Free syntax / explicit AST | Free object / initial algebra | interpreters agree on fixtures |
| New target surface must preserve old source behavior | Transported semantics | Left Kan / generated path | identity or embedding path preserves behavior |
| New internals must satisfy old views | Coherent observations | Right Kan / Yoneda | overlapping observations commute |
| New model must be viewed through old API | Restriction adapter | Precomposition / Delta | old golden tests pass through adapter |
| Public behavior is known before internals | Lifted implementation | Kan lift / realization | project(realize(case)) == required(case) |
| Public behavior determines internals and P supports building | Free builder behind projection | Freyd/AFT-style diagnostic | project(free(required(case))) satisfies required |
| Public behavior determines internals but P loses evidence | Obstruction report | failed lift/free-builder diagnostic | missing evidence/template/constraint named |
| Public policy implies internal checks | Residual obligations | Right-lift / weakest obligation | missing obligation fails projection |
| Stateful behavior unfolds over time | Behavioral coalgebra | coalgebra / observation over traces | trace law and invalid transition rejection |
| Operations need multiple handlers | Effect signature + handlers | algebraic effects / free operation syntax | handler observation parity |
| Generated payloads lose provenance | Generation path vocabulary | Coyoneda | lowering equals direct interpretation |
| Query/projection sprawl | Observation vocabulary | Yoneda | representation change preserves observations |
| Callbacks/closures cross boundaries | Explicit first-order IR | Defunctionalization | apply(encodedCase,x) == oldCallback(x) |
OUT

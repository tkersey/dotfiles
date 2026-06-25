# Read-Only Frontier Auditing

Use `actuation_frontier_auditor` at semantic-wave boundaries.

Trigger when:

```text
same owner/invariant reopens twice
multiple dimensions exist
multiple owners are plausible
proof mapping is unclear
selected wave has independent lock roots
```

Possible lanes:

```text
matrix:
  enumerate equivalence classes and missing rows

proof:
  map rows/tasks/laws to focused and aggregate proof

diff:
  determine whether the realized patch closes the selected class and leaves
  adjacent classes uncovered
```

Root remains the sole writer.

The auditor must emit structured evidence refs and a final call:

```text
frontier_ready
matrix_expand
proof_map_required
return_to_graph
blocked
```

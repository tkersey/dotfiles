# Proof DAG — PDAG-v1

PDAG records proof dependency and freshness. It is not permission to reuse stale green results.

```yaml
proof_dag:
  dag_version: PDAG-v1
  dag_id:
  artifact_state:
  nodes:
    - proof_id:
      kind:
        focused |
        wave |
        final
      command:
      covers:
        actuation_obligations: []
        matrix_rows: []
        files: []
        semantic_laws: []
      depends_on: []
      state:
        missing |
        running |
        pass |
        fail |
        stale |
        blocked
      epoch_ref:
      evidence_ref:
      invalidators: []
  gates:
    focused:
      required_nodes: []
      pass: yes | no
    wave:
      required_nodes: []
      pass: yes | no
    final:
      required_nodes: []
      pass: yes | no
```

## Cadence

```text
one mutation slice -> focused proof
completed semantic wave -> affected aggregate proof
final delivery head -> complete closure proof
```

## Freshness

A node is stale when any bound context changes:

```text
source/tree
dependencies
generated artifacts
toolchain
target/options
proof command
semantic route
selected matrix rows
```

## Reuse

Reuse only when:

- node state is pass;
- all dependencies pass;
- epoch/context is current;
- covered obligations did not change.

## DAG integrity

- IDs are unique.
- Dependencies reference known nodes.
- The graph is acyclic.
- Every required gate node exists.
- A gate passes only when all required nodes pass.

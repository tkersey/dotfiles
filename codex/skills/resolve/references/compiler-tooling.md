# Compiler Tooling

Structural tools:

```bash
resolve-c3 legacy-gate --file <legacy-cleanroom-artifact.yml>
resolve-c3 mrpc-gate --file <mrpc.json>
resolve-c3 rdr-gate --file <record.yml>
```

The cleanroom compiler gate scripts are retired. Current C3 structural authority is the controller-emitted MRPC-v1 plus RDR checks where a decision record is required.

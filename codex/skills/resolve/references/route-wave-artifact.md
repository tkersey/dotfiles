# Route-Wave Artifact

Publish route/RCP/RDP/NREC/negative-ledger/universalist decisions into a first-class artifact.

Preferred path:

```text
.ledger/proof/resolve/<resolve-run-id>/review-wave-<n>.route.yml
```

Validate with:

```bash
python codex/skills/review-compression-compiler/tools/route_wave_gate.py <route-wave-file>
```

If a decision is not in this artifact or a visible `Resolve route artifact:` line, it does not count for closure.

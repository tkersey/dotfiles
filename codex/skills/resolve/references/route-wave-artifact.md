# Route-Wave Artifact

Publish route/RCP/universalist decisions into a first-class artifact.

Preferred path:

```text
.step/proof/resolve/<resolve-run-id>/review-wave-<n>.route.yml
```

Validate with:

```bash
python codex/skills/review-compression-compiler/tools/route_wave_gate.py <route-wave-file>
```

If a route/RCP/universalist decision is not in this artifact or a visible `Resolve route artifact:` line, it does not count for closure.

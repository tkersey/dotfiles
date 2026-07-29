# STE-v1

`skill_tuning_evidence / STE-v1` is the passive evidence boundary between Seq
observation and `$tune` interpretation.

It carries:

- target and skill type;
- versions and contract authority;
- denominator;
- trigger quality;
- decision influence;
- clause compliance;
- downstream outcomes;
- repeated workarounds;
- recurrent gaps;
- positive/negative exemplars;
- limitations.

The canonical structural definition is:

```text
<tune-skill-root>/definitions/ledger/skill-tuning-evidence.json
```

Validate a packet with:

```bash
ledger validate \
  --definition <tune-skill-root>/definitions/ledger/skill-tuning-evidence.json \
  --input evidence=<ste.json> \
  --format json
```

The artifact contains `skill_tuning_evidence` plus its causality metadata. Seq's
generic result envelope owns producer identity, corpus identity, runtime stats,
limitations, and authority denial; it is not duplicated inside the artifact.

Seq reconstructs the evidence. Ledger establishes only that the packet is
structurally valid under the selected definition digest. `$tune` retains
interpretation and change-selection authority.

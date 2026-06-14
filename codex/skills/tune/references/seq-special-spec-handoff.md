# Seq Special-Spec Handoff

`$seq` CLI changes require a separate special spec.

When `$tune` discovers a `$seq` tooling gap, emit:

```yaml
seq_special_spec_handoff:
  spec_version: SEQ-SPEC-HANDOFF-v1
  need:
  observed_gap:
  required_behavior:
  command_shape:
  acceptance_criteria: []
  representative_validation: []
  source_evidence: []
```

Do not bundle `$seq` CLI implementation changes into ordinary `$tune` skill edits.

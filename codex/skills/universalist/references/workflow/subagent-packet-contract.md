# Universalist Specialist Payload

Universalist agents use the canonical `specialist-packet-v2` envelope in:

```text
codex/skills/references/specialist-packet-contract.md
```

Place Universalist-specific fields under `domain_payload`:

```yaml
domain_payload:
  candidate:
    summary:
    artifact: certificate | map | model | plan | none
  countercase:
    summary:
    disposition: defeats | narrows | survives | unresolved
  proof_obligations: []
  obstructions: []
  implementation:
    changed_files: []
    commands: []
    results: []
    stop_point:
```

Read-only roles omit `implementation`. The witness implementer and verifier report exact files and commands. No Universalist specialist emits a user-facing essay or recursively delegates.

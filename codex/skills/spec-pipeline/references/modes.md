# Modes

```text
full
gate-only
challenge-only
lint-only
repair
```

- `full`: create a decision-complete spec and authorize handoff only after all phases pass.
- `gate-only`: readiness judgment only; no spec and no mutation authority.
- `challenge-only`: one strongest invariant challenge only; no mutation authority.
- `lint-only`: implementation-readiness audit only; no mutation authority.
- `repair`: change only sections implicated by prior failed phases, then rerun required downstream phases.

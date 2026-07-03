# Probe Cases

Use these probes to test rewrite, naming, and safety behavior.

## Rewrite probes

### generic -> precise

Input:
```text
We should iterate on improvements to the skill until it gets better.
```

Expected:
```text
Find accretive changes to the skill until the contract is tighter.
```

### obligation preservation

Input:
```text
We may reject malformed inputs if they look risky.
```

Bad:
```text
Reject malformed inputs fail-closed.
```

Reason: changed `may` to an obligation.

Good:
```text
We may reject risky malformed inputs fail-closed.
```

### code-token preservation

Input:
```text
Run zig build check before opening the PR.
```

Expected: preserve `zig build check` exactly.

## Naming probes

Input:
```text
Things to Do Before Release
```

Expected candidates:
```text
Pre-Release Checklist
Release Readiness
Release Prep
Pre-Release Tasks
```

Input:
```text
A skill that drives a plan through tasks, fixed-point implementation, validation, and PR creation.
```

Expected candidates should include:
```text
actuating
```

## Doctrine probes

Input:
```text
Find a doctrine word for making a plan actually move to completion.
```

Expected: prefer `actuating`, not generic `execution`.

Input:
```text
Find a doctrine word for deleting code that no longer earns its place.
```

Expected: include `ablative` or `winnowing`; distinguish reduction from proof relation.

Input:
```text
Find a doctrine word for defunctionalization.
```

Expected: prefer `reifying`; include `totalizing` as interpreter-side companion.

## Safety probes

- Do not rewrite JSON/TOML/YAML keys for style.
- Do not rename code identifiers unless naming is explicitly requested and scope is clear.
- Do not remove uncertainty markers such as `probably`, `may`, `could`, `likely`, or `unknown` unless evidence changed.
- Do not make public-facing text more certain than the source.

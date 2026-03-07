# TK Shadow Pass - 2026-03-06

## Run
- Date: 2026-03-06
- Suite: `codex/skills/tk/references/eval/shadow-suite-2026-03-06.yaml`
- Machine gate: `uv run --with pyyaml python codex/skills/tk/scripts/tk_replay_benchmark.py --suite codex/skills/tk/references/eval/shadow-suite-2026-03-06.yaml`
- Result: `5/5` passed, `pass_rate=1.000`

## Rubric
- `pass`: preserves intended TK seam/shape behavior on that axis.
- `minor`: acceptable output, but monitor for recurrence.
- `fail`: drift that changes seam/shape, overclaims proof, or breaks the outer contract.

## Cases

### `shadow-advice-shared-parser`
- Mode: `advice`
- Session: `019cc521-151a-7b93-aa22-96d1c93280fd`
- Seam choice: `pass` - picks the shared import-boundary parser and explicitly justifies crossing one module to reach the real boundary.
- Abstraction level: `pass` - import-scoped parser seam, not a generic utility or wider framework.
- Blast radius: `pass` - keeps the cut local, suggests thin wrappers as a reversible first step.
- Proof posture: `pass` - proposes characterization plus thin integration checks; no faux execution claim.
- Output-contract compliance: `pass` - exact advice-mode section order.
- Drift: `none`
- Verdict: `pass`

### `shadow-advice-domain-hardening`
- Mode: `advice`
- Session: `019cc522-7c3f-70b0-ab53-c35dd10c7fa5`
- Seam choice: `pass` - chooses broker-ingress construction as the single refinement boundary.
- Abstraction level: `pass` - recommends a small typed ingress island (`DispatchCommand`) instead of a rewrite.
- Blast radius: `pass` - keeps scope to adapters plus ingress refinement.
- Proof posture: `pass` - uses constructor tests, exhaustive matching, and characterization checks; no overclaim.
- Output-contract compliance: `pass` - exact advice-mode section order.
- Drift: `none`
- Verdict: `pass`

### `shadow-implementation-summary`
- Mode: `implementation`
- Session: `019cc523-f69e-7801-b444-4bb4bcb1d38c`
- Seam choice: `pass` - anchors the rule in `parseTenantHeader(raw)` and deletes caller-local normalization.
- Abstraction level: `pass` - one parser seam, not broader middleware or a repo-wide migration.
- Blast radius: `pass` - narrows to the two handlers plus one job entrypoint.
- Proof posture: `pass` - explicitly says proof was not run, then gives exact commands and pass criteria.
- Output-contract compliance: `pass` - correct implementation-mode section order; `Incision` is a change summary, not a diff.
- Drift: `minor doctrine drift` - uses `Subtraction` as the named technique, which is outside the current creative-problem-solver picker list.
- Verdict: `pass`

### `shadow-strict-diff`
- Mode: `strict_output`
- Session: `019cc525-0f7e-7a20-8316-372900e947c8`
- Seam choice: `pass` - fixes normalization at the function boundary instead of pushing checks into callers.
- Abstraction level: `pass` - one-line local normalization change; no unnecessary helper extraction.
- Blast radius: `pass` - single-function diff.
- Proof posture: `pass` - no faux-proof prose appears; strict-output contract correctly suppresses TK chat sections.
- Output-contract compliance: `pass` - one fenced `diff` block and nothing else.
- Drift: `none`
- Verdict: `pass`

### `shadow-strict-no-diff`
- Mode: `strict_output`
- Session: `019cc525-439b-7fa0-b862-b6f14b42a9d3`
- Seam choice: `pass` - refuses to fake a local seam for a repository-wide rename outside scope.
- Abstraction level: `pass` - no invented workaround or docs-only pretend fix.
- Blast radius: `pass` - keeps blast radius at zero when scope is unsafe.
- Proof posture: `pass` - refuses unsafe movement instead of inventing a patch.
- Output-contract compliance: `pass` - exactly one `NO_DIFF:` line.
- Drift: `none`
- Verdict: `pass`

## Verdict
- Overall: `PASS`
- Seam/shape bar: `5/5` sampled sessions preserved the intended TK seam/boundary decision.
- Critical output-contract violations: `0`
- Faux-proof claims: `0`
- Follow-up: monitor the technique-name drift in `shadow-implementation-summary`; do not add a new replay case unless it recurs or starts affecting seam/shape decisions.

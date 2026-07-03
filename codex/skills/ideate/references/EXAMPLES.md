# Examples

## Example — diagnostic primitive escalated into a proof surface

### Compressed snapshot

- Scope: CLI safety tool with matcher rules.
- Primary surfaces: blocked-command CLI output, safety config, matcher tests.
- Evidence: matcher implementation, fixtures, README examples.
- Blind spot: no issue export.

### Opportunity map

#### Theme: Hidden matcher state is not user-visible

- Evidence: `src/matcher.ts`, `tests/matcher.test.ts`, README safety examples.
- Observation: matcher logic computes why a rule matched, but CLI output only says a command was blocked.
- Opportunity implied: expose a non-executing explanation/proof trace.
- Confidence: High.

### Escalation ledger

- Baseline idea: Add a pattern-testing CLI command.
- Why obvious loses: A test command helps debugging but does not preserve matcher behavior over time.
- Glaze material delta: Reframe as a canonical **policy proof surface** reused by diagnostics, golden tests, and support repros.
- ASI 10x frame: Make safety behavior explainable and falsifiable across users, maintainers, and future tools.
- Smallest proof-bearing artifact: A stable matcher explanation trace for one existing matcher fixture.
- Cash-out type: Proof surface + interface.
- First proof signal: Existing matcher fixtures produce stable explanation traces without changing enforcement behavior.

### Top idea

#### Canonical policy proof surface

- Category: DX / diagnostics / reliability.
- Evidence: matcher tests and docs imply users need to understand rule behavior.
- Originality source: hidden primitive + diagnostic inversion + proof surface.
- User / maintainer benefit: users debug without executing; maintainers gain behavior-preserving regression artifacts.
- Why this is not generic: tied to existing matcher semantics and safety configuration.
- Validation path: prototype output against current matcher fixtures.
- Overlap: net-new from available docs.

### Planning handoff seed excerpt

```md
# Planning Handoff Seed: Canonical Policy Proof Surface

## Thesis

Create a stable, non-executing matcher explanation artifact so safety policy behavior becomes explainable, testable, and reusable across user diagnostics, golden tests, and support workflows.

## Breakthrough Frame

- Baseline idea: Add a pattern testing CLI command.
- Glaze material delta: Reframe it as a canonical policy proof surface.
- ASI 10x horizon: Make safety policy behavior explainable and falsifiable across users, maintainers, and tools.
- Smallest proof-bearing artifact: A stable matcher explanation trace for one existing matcher path.
- Cash-out type: Proof surface + interface.
- First proof signal: Fixture-backed traces match current blocking behavior exactly.
```

### IDR-v1 excerpt

```yaml
ideate_result:
  receipt_version: IDR-v1
  mode: standard
  terminal_state: portfolio_ready
  evidence_sources_count: 5
  baseline_candidates_generated: 20
  candidates_shortlisted: 5
  glaze_gate:
    applied: yes
    material_delta_count: 3
  asi_gate:
    applied: yes
    cash_out_count: 2
  overlap_check:
    performed: yes
  chosen_direction: Canonical policy proof surface
  seed_emitted: yes
```

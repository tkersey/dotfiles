# Grading rubrics

## Material finding rubric
A material finding should usually satisfy at least one:
- correctness or soundness risk
- critical or major invariant strain
- meaningful misuse hazard
- verification gap that could reopen remediation
- consequential incidental complexity growth

## Typed evidence rubric
Every material finding should include:
- `recommended_change`: the exact change to make or validate
- `evidence_of_defect`: where the current state fails or risks failure
- `evidence_of_remedy`: why the proposed change actually addresses the defect
- `confidence`: `proven` | `plausible` | `speculative`
- `minimum_acceptable_fix`: the smallest change or check that would materially bound the issue
- `do_not_broaden_into`: what should stay out of scope unless new evidence appears

## Soundness ledger kinds
- `missing-witness`
- `stale-witness`
- `contradictory-witness`
- `preservation-break`
- `stuck-state`
- `impossible-state`
- `partial-elimination`
- `overclaim`
- `incoherence`
- `non-compositional`

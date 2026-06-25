# Mode Contracts

## Survey — CBS-v1

A provisional repository/system map, evidence references, exact next questions,
and user judgments. It explicitly carries `no_committed_portfolio: yes`.

## Doctrine and deep — CBD-v2

The complete closed doctrine graph. Deep mode additionally requires accepted
specialist receipts.

## Refresh — CBDD-v1

A partition of retained, modified, added, and invalidated doctrine IDs between
two valid CBD-v2 artifacts. It records changed paths, proof rechecks, and intent
drift.

## Portfolio — CBP-v1

A knowledge-routing and skill-candidacy decision report under an existing valid
doctrine. It does not re-run the complete repository analysis unless the
underlying doctrine is stale.

## Audit — CBA-v1

A conformance report comparing current guidance, skills, and enforcement
surfaces with doctrine. Audit is not an alias for refresh.

Validate non-CBD modes with:

```bash
uv run --with pyyaml python \
  codex/skills/codebase-doctrine/tools/mode_gate.py artifact.yaml
```

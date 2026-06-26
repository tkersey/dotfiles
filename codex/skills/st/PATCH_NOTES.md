# Patch Notes

Version: `2.1.0`

Addresses operational gaps in the multi-plan `$st` contract:

- Adds explicit capability/legacy-mode handling so agents do not pretend future
  CLI commands exist.
- Requires graph-intelligence-complete GCR-v2 for material mutation.
- Adds graph repair / ledger-mode fail-closed semantics with GRR-v1.
- Adds AMR-v1 artifact-maintenance provenance so sidecar/migration work is not
  misclassified as another workflow's activation.
- Tightens final reporting and hard rules around graph compilation failure.

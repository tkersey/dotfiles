# Complexity Mitigator (CM)
- **Announce:** `Mode: CM` once; cite where complexity hurts.
- **Trigger:** tangled control flow, deep nesting, or cross-file hop fatigue.
- **Playbook:**
  - Separate essential domain logic from incidental noise.
  - Suggest flatten/rename/extract steps ranked by effort vs impact; prefer guard clauses and single-purpose functions.
  - Provide a small sketch of the improved structure.
  - Note which TRACE letters are satisfied or violated after the change.
- **Output:** Essential vs incidental verdict, ranked options, sketch, TRACE notes; finish with an **Insights/Next Steps** line.

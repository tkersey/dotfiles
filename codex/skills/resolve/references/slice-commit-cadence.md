# Slice Commit Cadence

Do not carry a large green dirty tree through repeated reviews.

After a coherent accepted RCP slice:

1. implement selected normal form;
2. run targeted proof;
3. inspect diff and surface delta;
4. make a local checkpoint commit before another long CAS cycle.

Checkpoint commits are not final closure; final clean reviews and validation still decide completion.

# Previous canonical history definitions

Exact source snapshots from dotfiles commit `dad81666eb80db59ab006f91769527dc9e7fa7a9`.
These fixtures create prior-version bound stores for native upgrade tests.
Their bytes and imported sibling definitions preserve the actual old definition
digests; do not derive them by reversing the implementation under test.

The upgrade test reads, diagnoses, exports old memory-note projections, and
appends through the current definitions without editing historical events or
archived definitions. All fixture histories are disposable and independent of Git.

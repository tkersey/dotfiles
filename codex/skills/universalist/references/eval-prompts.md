# Universalist eval prompts

Use these prompts to test that the skill climbs only when a stronger shape is truly cheaper.

## Should trigger

### Nullable lifecycle fields

Prompt: "This model has `status` plus `approvedAt`, `publishedAt`, `deletedAt`, and several nullable fields. What structural refactor should we do?"

Expected:

- identify coproduct/tagged union candidate;
- choose decoder or DTO mapper as first seam;
- preserve wire/storage shape unless breaking change is approved;
- include invalid fixture tests;
- mention runtime-only leftovers if language cannot enforce exhaustiveness.

### Repeated boundary validation

Prompt: "Every controller trims, lowercases, regex-checks, and validates the same email string."

Expected:

- refined/equalizer value at parse/constructor boundary;
- valid/invalid/normalization proof;
- post-lift reduction opportunity to delete duplicate validators.

### Shared tenant agreement

Prompt: "We keep checking that customer.tenantId equals subscription.tenantId."

Expected:

- pullback witness or checked aggregate constructor;
- mismatch rejection test;
- preserved projections;
- no broad rewrite.

### Syntax and execution mixed

Prompt: "Rules are stored, evaluated, rendered, and explained by the same branchy class."

Expected:

- free construction / AST only if multiple interpreters are real;
- one interpreter first;
- differential/parity tests;
- no HKT-heavy design.

### Split move

Prompt: "A React SPA has two static pages and one multi-step checkout flow. Can we simplify it?"

Expected:

- route to split: descend React/build layer if evidence supports it;
- preserve or lift checkout lifecycle into reducer/state table;
- proof via behavior parity and invalid-transition tests.

## Should not trigger or should hold

### One-off branch

Prompt: "This function has one `if` statement for a rare edge case. Should we create a strategy abstraction?"

Expected: reject exponential; keep direct conditional or local function.

### Unstable rule

Prompt: "Product is still deciding what counts as a valid account slug. Should we add a refined type now?"

Expected: hold; keep local validation until predicate stabilizes.

### Framework tax is the main problem

Prompt: "This app uses a framework and bundler for mostly static pages. I want fewer layers."

Expected: route to `reduce`; do not invent a new domain model unless an invariant signal appears.

### Pair checked once

Prompt: "One handler asserts two IDs match in one place. Should this be a pullback?"

Expected: probably no; local assertion near join is enough unless repeated/cross-boundary evidence appears.

## Scoring rubric for evals

A good answer includes:

- correct move classification: climb, descend, hold, or split;
- first seam;
- proof signal;
- boundary compatibility;
- reduction preflight;
- no repo-wide rewrite;
- no category jargon without engineering behavior.

# Reduce eval prompts

Use these prompts to test that the skill reduces only incidental tax and preserves essential truth.

## Should trigger

### Static React app

Prompt: "This app has React and Vite, but only two static pages and one contact form. Can we remove React?"

Expected:

- audit React/build layer;
- recommend possible descent to HTML/CSS/native JS if evidence supports it;
- native forms/constraint validation as candidate primitive;
- behavior parity proof such as form submission fixture, screenshot/accessibility smoke checks, or route checks;
- rollback via branch/revert or preserved static build path.

### Codegen surface too large

Prompt: "This generated client creates 20k lines but only 3 endpoints are used."

Expected:

- inventory generated surface and call sites;
- slice unused endpoints or replace with narrow handwritten client;
- preserve schema/contract tests;
- no delete without proof.

### DI with one implementation

Prompt: "Every interface has one implementation and the DI container makes changes hard."

Expected:

- composition root extraction;
- direct constructors/explicit parameters;
- keep interfaces only where variants are real;
- first seam and rollback.

### GraphQL forwarding gateway

Prompt: "This GraphQL gateway only forwards one internal call, but external clients use its schema."

Expected:

- external risk medium/high;
- no immediate delete;
- wrap/compatibility plan;
- contract-first replacement or hold.

### Split move with protocol

Prompt: "A workflow engine manages a four-step checkout but most of its features are unused. Can we simplify?"

Expected:

- essential protocol check;
- transition table;
- reduce wrapper maybe to reducer/job queue;
- do not flatten to optional fields.

## Should hold or hand off

### Missing invariant shape

Prompt: "This model has `status` plus five nullable fields. Can we reduce it?"

Expected:

- do not flatten further;
- hand off to `universalist` or recommend coproduct behind decoder;
- maybe reduce surrounding wrappers only after invariant is preserved.

### Unknown external obligation

Prompt: "Delete this API gateway; it seems useless."

Expected:

- ask for or inspect client/contracts;
- external risk unknown/high;
- cap at wrap/slice/hold until proof exists.

### One local helper

Prompt: "Can we reduce this small helper function?"

Expected:

- not a reduce trigger unless framed as layer removal;
- normal refactor or no action.

## Scoring rubric for evals

A good answer includes:

- evidence ledger;
- `T/V/D` and confidence;
- external obligation risk;
- essential abstraction check;
- verdict;
- lower primitive;
- first safe seam;
- proof and rollback;
- no personal-preference-only cuts.

# Codebase Signal Lanes

Use these lanes to find original, evidence-backed ideas for changes, additions, and refactors. Do not treat every signal as a problem. Treat each signal as a prompt for candidate generation.

## 1. Public surface lane

Inspect commands, routes, exported APIs, UI entry points, examples, docs, screenshots, config schemas, and public error messages.

Ask:

- What can users currently do?
- What can the internals do that users cannot access?
- Where are errors, diagnostics, or recovery paths weak?
- What examples imply a missing affordance?
- What public name promises more than the implementation delivers?

Common opportunity shapes:

- safe preview or dry-run mode
- explain command or diagnostic endpoint
- discoverability improvement
- narrower API that wraps a fragile low-level primitive
- better failure recovery flow

## 2. Maintainer friction lane

Inspect package scripts, setup docs, CI workflows, test fixtures, local tooling, generated files, and manual release steps.

Ask:

- What takes too many steps?
- What is hard to reproduce locally?
- What failure gives poor feedback?
- What repeated setup could become a first-class command?
- What maintenance step relies on memory instead of tooling?

Common opportunity shapes:

- one-shot setup or doctor command
- fixture factory or test harness simplification
- deterministic local reproduction workflow
- CI failure triage output
- release checklist automation

## 3. Architecture seam lane

Inspect large modules, duplicated concepts, repeated adapters, circular imports, config boundaries, domain objects, and code that knows too much about distant layers.

Ask:

- Where does the same concept appear under multiple names?
- Which boundary leaks implementation detail?
- Which adapter or mapper pattern repeats?
- What refactor would make the next feature easier?
- What behavior-preserving change would remove more code than it adds?

Common opportunity shapes:

- extract shared parser/validator/adapter
- consolidate config resolution
- split a large god module around a stable seam
- unify domain naming
- introduce a narrow internal interface where duplication already exists

## 4. Test-intent lane

Read tests as product and architecture documentation. Inspect snapshots, fixtures, helper utilities, coverage gaps, and high-setup tests.

Ask:

- What behavior is important enough to test?
- What critical path lacks tests?
- What fixtures reveal awkward architecture?
- What repeated test setup suggests a missing abstraction?
- What golden output could protect behavior before refactoring?

Common opportunity shapes:

- golden test harness for behavior-preserving refactor
- test fixture simplification
- contract tests around public API boundaries
- regression coverage for high-risk edge cases
- executable examples that double as docs

## 5. Reliability lane

Inspect validation, retries, cleanup, partial failure, idempotency, concurrency, persistence, migrations, external calls, and background work.

Ask:

- What breaks halfway?
- What state can become inconsistent?
- What assumption is not validated at the boundary?
- What operation needs idempotency but does not clearly have it?
- What should be observable but is silent?

Common opportunity shapes:

- recovery or resume path
- boundary validation hardening
- idempotency key or duplicate protection
- cleanup guarantee
- structured failure result instead of opaque exception

## 6. Performance lane

Inspect startup, hot loops, repeated I/O, serialization, caching, batching, dependency loading, large test suites, and build times.

Ask:

- What work repeats unnecessarily?
- What scales with project size, user data, or repository size?
- What could be measured cheaply before optimizing?
- What command feels slow because it does too much before producing feedback?
- What cache or batch point is implied by repeated code?

Common opportunity shapes:

- measurement-first performance probe
- lazy loading or deferred expensive work
- cache with explicit invalidation boundary
- batch API or grouped I/O
- faster smoke-test or partial-build path

## 7. Observability and diagnostics lane

Inspect logs, errors, debug flags, telemetry hooks, status output, internal state machines, and support documentation.

Ask:

- What internal state exists but is not exposed helpfully?
- What would a user or maintainer need during failure triage?
- Which error message tells what failed but not what to do next?
- What hidden decision could be rendered as an explanation?
- What support question could a diagnostic command answer automatically?

Common opportunity shapes:

- doctor command
- explain mode
- structured error with remediation
- verbose trace for one subsystem
- health/status endpoint

## 8. Negative-space lane

Look for names, docs, TODOs, tests, type names, examples, and directory structure that imply missing capabilities.

Ask:

- What does the code seem to want to become?
- What internal abstraction is under-exposed?
- What user-facing primitive is almost there?
- What word appears repeatedly without a first-class representation?
- What workflow is documented by example but not supported directly?

Common opportunity shapes:

- promote internal primitive to public feature
- add missing command around existing core logic
- create first-class concept from repeated string/config patterns
- formalize an implicit workflow
- turn examples into supported templates

## 9. History lane

Use git history when available. Inspect recent churn, repeated fixes, reverts, renamed concepts, abandoned files, and commit messages around the same subsystem.

Ask:

- What files churn most?
- What bugs recur?
- What was reverted?
- What concept keeps being renamed or reinterpreted?
- What subsystem absorbs unrelated changes because boundaries are weak?

Common opportunity shapes:

- stabilize a churn-heavy boundary
- isolate a recurring bug class
- write characterization tests before refactoring
- rename or split confused concepts
- reduce blast radius around a high-change subsystem

## 10. Refactor-enabler lane

Find simplifications that unlock future work rather than refactors that merely look cleaner.

Ask:

- What behavior-preserving change would reduce future risk?
- What duplication blocks confident feature work?
- What abstraction would remove more code than it adds?
- What invariant should become explicit before adding features?
- What seam would make testing easier?

Common opportunity shapes:

- behavior-preserving consolidation
- invariant extraction
- adapter boundary
- golden-output safety net
- delete or collapse obsolete paths

## Evidence capture format

Prefer this compact form:

```md
Signal
- Lane:
- Evidence: `path:line` or smallest file/symbol scope
- Observation:
- Candidate ideas it could seed:
- Confidence: High | Medium | Low
```

## Escalation prompts by lane

After harvesting signals, use these prompts to find Glaze/ASI-grade opportunities:

- **Public surface → interface shift**: What command, endpoint, API, or UI surface would turn hidden internal capability into a first-class user interaction?
- **Maintainer friction → coordination shift**: What small tool or protocol would let maintainers coordinate around the system instead of relying on memory and convention?
- **Architecture seam → invariant shift**: What invariant, if made explicit, would eliminate a recurring class of bugs or simplify future features?
- **Test intent → proof surface**: What executable artifact could make the system's most important behavior measurable before further change?
- **Reliability → recovery primitive**: What small mechanism would make partial failure survivable, explainable, or reversible?
- **Performance → measurement primitive**: What probe would reveal whether optimization is worth doing before committing to a performance project?
- **Observability → diagnostic inversion**: What internal decision or state could be exposed safely so users or maintainers can debug the system themselves?
- **Negative space → hidden product**: What capability is already implied by names, tests, docs, or types but has not been promoted into a product surface?
- **History → strategic ordering**: What sequence of changes would turn a churn-heavy area into a stable platform for future work?
- **Refactor-enabler → behavior-preserving unlock**: What small refactor would create the proof surface or invariant needed for a later bolder move?

A signal is especially valuable when it can become one of:

- a mechanism that changes system behavior
- an interface or protocol that changes coordination
- a proof surface that makes progress measurable
- a strategy that changes sequencing, incentives, or leverage

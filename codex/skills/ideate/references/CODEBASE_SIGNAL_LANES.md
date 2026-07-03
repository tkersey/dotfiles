# Codebase Signal Lanes

Use these lanes to find original, evidence-backed opportunities. Do not treat every signal as a problem. A signal seeds hypotheses; verify before ranking.

## Evidence capture

```md
Signal
- Lane:
- Evidence: `path:line` or smallest file/symbol/command/test scope
- Observation:
- Candidate ideas it could seed:
- Confidence: High | Medium | Low
```

## 1. Public surface lane

Inspect commands, routes, exported APIs, UI entry points, examples, docs, screenshots, config schemas, and public errors.

Ask: What can users do? What can internals do that users cannot access? Where are diagnostics weak? What examples imply a missing affordance?

Common shapes: dry-run/preview, explain command, discoverability, recovery flow, wrapper around hidden primitive.

## 2. Maintainer friction lane

Inspect package scripts, setup docs, CI, test fixtures, generated files, manual release steps.

Ask: What takes too many steps? What is hard to reproduce? What failure gives poor feedback? What relies on memory?

Common shapes: doctor command, fixture factory, local repro workflow, CI triage output, release automation.

## 3. Architecture seam lane

Inspect large modules, duplicated concepts, repeated adapters, config boundaries, domain objects, circular imports, and code that knows too much.

Ask: Where does a concept appear under many names? Which boundary leaks? What behavior-preserving change unlocks future work?

Common shapes: shared parser/validator/adapter, config consolidation, boundary split, naming unification, narrow internal interface.

## 4. Test-intent lane

Read tests as product/architecture documentation.

Ask: What behavior is important enough to test? What critical path lacks tests? What fixtures reveal awkward architecture?

Common shapes: golden harness, fixture simplification, contract tests, regression coverage, executable examples.

## 5. Reliability lane

Inspect validation, retries, cleanup, partial failure, idempotency, concurrency, persistence, migrations, external calls, and background work.

Ask: What breaks halfway? What can become inconsistent? What assumption is not validated? What should be observable but is silent?

Common shapes: recovery/resume, boundary validation, idempotency key, cleanup guarantee, structured failure result.

## 6. Performance lane

Inspect startup, hot loops, repeated I/O, serialization, caching, batching, dependency loading, large tests, and build times.

Ask: What repeats unnecessarily? What scales with repo/user data? What could be measured cheaply first?

Common shapes: measurement probe, lazy loading, explicit cache boundary, batch API, faster smoke path.

## 7. Observability and diagnostics lane

Inspect logs, errors, debug flags, status output, internal state machines, and support docs.

Ask: What internal state exists but is not exposed helpfully? Which error says what failed but not what to do next?

Common shapes: doctor command, explain mode, structured remediation, subsystem trace, status endpoint.

## 8. Negative-space lane

Look for names, docs, TODOs, tests, examples, and directories that imply missing capabilities.

Ask: What does the code seem to want to become? What hidden primitive is under-exposed? What word appears repeatedly without a first-class representation?

Common shapes: promote internal primitive, add command around existing core logic, formalize implicit workflow, supported template.

## 9. History / churn lane

Use git history when available.

Ask: What files churn most? What bugs recur? What was reverted? What concept keeps being renamed?

Common shapes: stabilize boundary, isolate recurring bug class, characterization tests, rename/split confused concepts.

## 10. Refactor-enabler lane

Find simplifications that unlock future work rather than refactors that merely look cleaner.

Ask: What behavior-preserving change reduces future risk? What invariant should become explicit before adding features?

Common shapes: consolidation, invariant extraction, adapter boundary, golden-output safety net, deletion/collapse of obsolete paths.

## Escalation prompts by lane

- Public surface -> interface shift
- Maintainer friction -> coordination shift
- Architecture seam -> invariant shift
- Test intent -> proof surface
- Reliability -> recovery primitive
- Performance -> measurement primitive
- Observability -> diagnostic inversion
- Negative space -> hidden product
- History -> strategic ordering
- Refactor-enabler -> behavior-preserving unlock

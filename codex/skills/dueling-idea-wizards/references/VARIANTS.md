# Duel Mode Variants

The default `--mode=ideas` runs the standard Idea Wizard prompt. These variants swap the ideation prompt for domain-specific versions while keeping the cross-scoring and reveal mechanics identical.

## Architecture Mode (`--mode=architecture`)

```text
Analyze this project's architecture deeply. Come up with your 30 best ideas for architectural improvements -- refactors, better abstractions, cleaner separations of concern, more maintainable patterns, reduced coupling, improved testability, better error boundaries, smarter use of the type system, and structural changes that would make the codebase significantly easier to reason about, extend, and maintain. Think through each carefully: what would change, what would break, what would get easier, what would the migration path look like. Winnow to your top $NUM_TOP architectural proposals, ordered best to worst, with full rationale. Write to WIZARD_IDEAS_[TYPE].md. Use ultrathink.
```

**Best for:** Projects with accumulated tech debt, pre-rewrite planning, "where should we go from here" decisions.

## Security Mode (`--mode=security`)

```text
Perform a thorough security analysis of this project. Come up with your 30 best ideas for security hardening -- attack surface reduction, input validation improvements, authentication/authorization strengthening, secrets management, dependency security, injection prevention, rate limiting, audit logging, threat modeling gaps, and defensive coding patterns. For each idea, describe the threat it mitigates, the likelihood and impact, and the implementation complexity. Winnow to your top $NUM_TOP security improvements, ordered by risk-reduction value. Write to WIZARD_IDEAS_[TYPE].md. Use ultrathink.
```

**Best for:** Pre-launch security review, post-incident hardening, compliance preparation.

## UX/Ergonomics Mode (`--mode=ux`)

```text
Evaluate this project from the perspective of every type of user who interacts with it -- developers, operators, end users, new contributors, and AI coding agents. Come up with your 30 best ideas for UX and ergonomic improvements -- better defaults, clearer error messages, reduced cognitive load, smoother onboarding, more intuitive APIs, better documentation integration, smarter help output, improved discoverability of features, and friction reduction in common workflows. Think through how users currently experience each pain point and how your improvement changes that experience. Winnow to your top $NUM_TOP UX improvements. Write to WIZARD_IDEAS_[TYPE].md. Use ultrathink.
```

**Best for:** CLI tools, developer SDKs, anything where "easy to use" is a competitive advantage.

## Performance Mode (`--mode=performance`)

```text
Profile this project's likely performance characteristics through code analysis. Come up with your 30 best ideas for performance optimization -- hot path improvements, algorithmic complexity reductions, caching opportunities, lazy initialization, batch processing, memory allocation reduction, I/O optimization, parallelization opportunities, and startup time improvements. For each idea, estimate the expected speedup and the effort required. Be specific about WHERE the bottleneck is and WHY your fix helps. Winnow to your top $NUM_TOP optimization opportunities, ordered by impact/effort ratio. Write to WIZARD_IDEAS_[TYPE].md. Use ultrathink.
```

**Best for:** Performance-sensitive code, latency optimization, "why is this slow" investigation.

## Reliability Mode (`--mode=reliability`)

```text
Analyze this project for reliability and resilience gaps. Come up with your 30 best ideas for improving reliability -- error handling improvements, retry logic, graceful degradation, circuit breakers, timeout management, resource leak prevention, crash recovery, data integrity protection, idempotency guarantees, and observability improvements. For each idea, describe the failure mode it prevents and the blast radius of that failure today. Winnow to your top $NUM_TOP reliability improvements. Write to WIZARD_IDEAS_[TYPE].md. Use ultrathink.
```

**Best for:** Production services, infrastructure tools, anything that must not go down.

## Innovation Mode (`--mode=innovation`)

```text
Think radically about this project. Forget incremental improvements -- come up with your 30 boldest ideas for what this project COULD become. Think about entirely new capabilities, surprising integrations, paradigm shifts in how users interact with it, cross-domain applications nobody has considered, and ways to make it 10x more valuable rather than 10% better. Include at least 5 ideas that sound almost crazy but might actually work. Winnow to your top $NUM_TOP breakthrough ideas, ordered by potential impact (not feasibility -- we'll worry about that during cross-scoring). Write to WIZARD_IDEAS_[TYPE].md. Use ultrathink.
```

**Best for:** Roadmap brainstorming, "what's next" planning, breaking out of incremental thinking.

## Cross-Scoring Remains the Same

Regardless of mode, the cross-scoring prompt (Phase 5) is identical. The scoring criteria naturally adapt because agents evaluate ideas in context. An architecture idea gets scored on architectural merit; a security idea gets scored on threat reduction.

The reveal prompt (Phase 6) is also identical. The adversarial dynamics work regardless of domain.

## Combining Modes with --focus

Modes and focus can be combined:
- `--mode=security --focus="authentication layer"` narrows security ideation to auth
- `--mode=ux --focus="CLI onboarding experience"` targets UX analysis at first-run
- `--mode=performance --focus="database queries"` limits optimization ideas to DB layer

## Multi-Mode Dueling (Advanced)

For comprehensive analysis, run multiple mode-specific duels across rounds:

```
Round 1: --mode=ideas (broad)
Round 2: --mode=security (deep)
Round 3: --mode=architecture (structural)
```

Each round produces its own set of artifacts with round suffixes. The final synthesis aggregates across all rounds, noting which ideas appeared in multiple modes (extremely high confidence) and which are mode-specific.

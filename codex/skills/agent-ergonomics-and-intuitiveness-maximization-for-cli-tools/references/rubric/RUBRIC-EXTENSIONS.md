# RUBRIC-EXTENSIONS — Adding project-specific dimensions

The default rubric has 11 dimensions. Some projects need more: security, performance, accessibility, internationalization. This file gives the framework for extending the rubric without forking the skill.

---

## When to extend

Add a custom dimension when:

- The project has a **regulated** concern (e.g. security audit pressure, accessibility laws)
- The project has a **business-critical** non-functional requirement (e.g. p95 latency for a hot-path hook)
- The project competes on a **specific axis** (e.g. localization for international SaaS)

Don't add a dimension just because it sounds nice. The 11 defaults cover most agent-ergonomic concerns.

---

## How to extend (mechanical)

1. **Edit `references/rubric/SCORING-RUBRIC.md`.**
   - Add the new dimension at the bottom
   - Define anchors at 0/250/500/750/1000
   - Cite an exemplar (or counter-example) at each anchor
   - Update `weighted_score` formula if changing weights
2. **Bump `rubric_version`** in `audit/manifest.json`.
3. **Update SCORING-RUBRIC.md's "default weighting"** if the extension changes the mean.
4. **Update `tools/validate_scorecard.sh`** to know about the new dim.
5. **Update IO-CONTRACTS.md** to document the new field in `agent_surfaces.jsonl`.
6. **Re-score from scratch** using the new rubric_version.
7. **Document the extension** in HANDOFF.md so future passes know.

---

## Common extensions

### Extension A: Security (for security-critical CLIs)

**Use when.** The CLI handles credentials, executes untrusted input, has admin verbs.

**Anchors:**

```
0:    Tool runs untrusted input as shell. Logs credentials. No --no-network mode.
250:  Some sanitization. Credentials redacted in --verbose. No `--no-network`.
500:  Credentials never logged. Untrusted input quoted. Has `--no-network` flag.
750:  All of 500 PLUS: SBOM exposed; security-relevant flags documented in capabilities;
      input validation at boundaries; CSRF/XSS-flavored protections where applicable.
1000: All of 750 PLUS: Cryptographic identity for privileged ops; audit log for
      privileged actions; security-event taxonomy in capabilities.
```

**Weight.** 1.5× for security-critical tools.

### Extension B: Performance (for hot-path CLIs)

**Use when.** The CLI is invoked per-keystroke (hooks), per-build (build tools), or in tight loops.

**Anchors:**

```
0:    Canonical invocation > 500ms.
250:  Canonical invocation 100–500ms.
500:  Canonical invocation 10–100ms. Cold start is acceptable.
750:  Hot path < 10ms with quick-reject filter. Cold start documented.
1000: All of 750 PLUS: per-call latency budget published; trace file for profiling;
      regression budget enforced in CI.
```

**Weight.** 2× for hot-path CLIs (e.g. dcg).

### Extension C: Accessibility (for human + agent CLIs)

**Use when.** The CLI is also used by humans with accessibility needs (screen readers, low vision, cognitive accessibility).

**Anchors:**

```
0:    All output assumes color/visual. ANSI-only progress bars. ASCII art only.
250:  Honors NO_COLOR. ASCII-only mode available.
500:  Honors NO_COLOR + TERM=dumb. ASCII-only mode is default in non-TTY. Plain-text spinner alternative.
750:  All of 500 PLUS: Output structured for screen readers (no ASCII tables that don't read well aloud);
      verbose-mode that explains the visual UI in prose.
1000: All of 750 PLUS: --speak mode that produces narrated output; --screen-reader-friendly default
      detection.
```

**Weight.** 1.0× for general tools; 1.5× for tools claiming a11y compliance.

### Extension D: Internationalization (for multi-language CLIs)

**Use when.** The CLI ships in multiple languages (locale-aware output).

**Anchors:**

```
0:    English-only. Locale not detectable. No --lang flag.
250:  Honors LC_ALL but only for limited strings.
500:  Translated `--help` text. UTF-8 input handled correctly.
750:  All of 500 PLUS: per-language test fixtures; --lang flag documented; capabilities lists
      supported_languages.
1000: All of 750 PLUS: bidirectional text support; CJK width-aware tables;
      context-sensitive translations (not just word-by-word).
```

**Weight.** 1.0× for general; 2× for tools targeting global audience.

### Extension E: Telemetry transparency (for tools that phone home)

**Use when.** The CLI sends usage data to vendor servers.

**Anchors:**

```
0:    Phones home; no opt-out; logs sensitive data.
250:  Phones home; opt-out via undocumented env var.
500:  Phones home; documented opt-out (DO_NOT_TRACK + tool-specific); no PII collected.
750:  All of 500 PLUS: telemetry doc in capabilities (data_collected, endpoint, policy_url);
      first-run consent prompt.
1000: All of 750 PLUS: per-event consent; user-readable telemetry log; ability to inspect what
      would be sent before sending.
```

**Weight.** 1.0× for general; 2× for enterprise tools.

### Extension F: Cross-platform consistency (for tools shipping on Linux + Mac + Windows)

**Use when.** The CLI claims to work on multiple OSes.

**Anchors:**

```
0:    Different exit codes / output / behavior per OS.
250:  Mostly the same; some platform-specific quirks documented.
500:  Same exit codes + output; platform-specific behavior gated behind explicit flags.
750:  All of 500 PLUS: capabilities lists per-platform features; tests run on all platforms in CI.
1000: All of 750 PLUS: cross-platform regression tests; platform-specific paths documented.
```

**Weight.** 1.5× for tools claiming cross-platform support.

### Extension G: SDK consistency (for tools with library + CLI)

**Use when.** The tool ships both a library SDK and a CLI wrapper.

**Anchors:**

```
0:    SDK and CLI behave differently for same operations.
250:  Mostly aligned; per-call divergences documented.
500:  CLI is generated from SDK. Same input shapes produce same outputs.
750:  All of 500 PLUS: cross-surface schema-pin tests; capabilities exposes SDK info.
1000: All of 750 PLUS: SDK and CLI share canonical examples; both have same error pedagogy.
```

**Weight.** 1.5× for tools with both surfaces.

---

## Weighting strategy

Default: every dim weight 1.0×. Custom dim's weight is the project's call.

Example weighting for a security-critical hot-path hook (dcg-flavored):

```yaml
weights:
  agent_intuitiveness:        1.5
  agent_ergonomics:           1.0
  agent_ease_of_use:          1.0
  output_parseability:        1.5
  error_pedagogy:             2.0    # critical for agents
  intent_inference:           1.0
  safety_with_recovery:       1.5
  determinism:                1.5
  self_documentation:         1.0
  composability:              1.5
  regression_resistance:      1.0
  # custom dim
  security:                   2.0    # security-critical
  performance:                2.0    # hot path
```

`weighted_score = sum(score_i × weight_i) / sum(weight_i)`.

Document weights in `phase0_scope_decision.md`.

---

## Validating extensions

`tools/validate_scorecard.sh` should know about all dims:

```bash
# In validate_scorecard.sh, the dim list is hardcoded. When adding extensions,
# update the list AND any project-specific scripts.

DEFAULT_DIMS=(agent_intuitiveness agent_ergonomics agent_ease_of_use \
              output_parseability error_pedagogy intent_inference \
              safety_with_recovery determinism_and_reproducibility \
              self_documentation composability regression_resistance)

PROJECT_DIMS=(security performance)   # project-specific extensions

ALL_DIMS=("${DEFAULT_DIMS[@]}" "${PROJECT_DIMS[@]}")
```

---

## Cross-pollination

When you find an extension is broadly applicable beyond one project, consider promoting it:

1. Document the extension in this file
2. Add anchor levels with concrete examples
3. Add to the default rubric (becomes dim 12, 13, ...) IF the user agrees and the project landscape would benefit

The 11 defaults were once just "common patterns observed across exemplars." Extensions follow the same path.

---

## When NOT to extend

Don't extend if:
- The concern is already covered by existing dims (e.g. "user-friendly" is mostly intuitiveness + ease_of_use + error_pedagogy)
- The concern doesn't have observable, anchored levels (vague "feel good" criteria don't score)
- The concern is a one-off and won't be re-scored

The default 11 + 7 common extensions usually cover what's needed.

---

## Extending the operator library too

If a new dim has new failure patterns, add operators:

- `🔒` Security-Hardened — for security extension
- `⚡` Latency-Budget — for performance extension
- `♿` Accessible-Mode — for accessibility extension
- `🌍` Locale-Aware — for i18n extension

Operators follow the same shape as the existing 33 (see OPERATORS.md). Add to OPERATORS.md AND to the composition cheat-sheet for the new dim.

---

## Cross-references

- `references/rubric/SCORING-RUBRIC.md` — the default 11 dims
- `references/methodology/OPERATIONALIZING-EXPERTISE-TRACK-A.md` — how the rubric IS the kernel
- `references/methodology/CONTINUOUS-IMPROVEMENT.md` — annual rubric refresh
- `references/methodology/CLI-ARCHETYPES.md` — per-archetype dimension weight overrides (orthogonal axis)
- `references/methodology/AGENT-PROFILES.md` — per-agent-profile weight overrides (orthogonal axis)

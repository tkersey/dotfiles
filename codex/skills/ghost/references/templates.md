# Ghost Library Artifact Templates

Ghost libraries ship specifications and tests, not implementation code.

## SPEC.md (outline)
- Title + version
- Overview (what the library does)
- Design principles (deterministic, pure, etc.)
- Type conventions (abstract types and normalization rules)
- Error handling (language-idiomatic, exact error conditions)
- Operations (public API)
  - Operation id
  - Signature
  - Arguments and options
  - Behavior rules and thresholds
  - Edge cases
  - Examples (short, non-exhaustive)
- Testing section (reference tests.yaml format)

## tests.yaml (format)

```yaml
version: "X.Y.Z"  # upstream library version or revision (opaque string)

operation_id:
  - name: "human-readable case"
    input: { ... }  # may also be a scalar/sequence for single-arg operations
    output: ...
  - name: "error case"
    input: { ... }
    error: true
```

### Operation ids
- Use stable ids that map cleanly across languages:
  - `foo` (top-level function)
  - `module.foo` (namespaced function)
  - `Class#method` (instance method)
  - `Class.method` (static/class method)

Notes:
- `version` identifies the upstream library version used as evidence (SemVer/tag if available; otherwise a stable source revision like `git:<short-sha>`).
- Use explicit timestamps/values; avoid "now" or system state.
- Inputs must be deterministic and YAML-serializable (scalars, sequences, maps).
- For bytes/buffers, encode as hex or base64 string (document which in `SPEC.md`).
- Avoid YAML-only features (anchors, tags, custom types); quote ambiguous scalars (`yes`, `no`, `on`, `off`, `null`).
- `output` and `error` are mutually exclusive.
- Represent errors with `error: true` only.

## INSTALL.md (outline)
- Short intro: "This is a ghost library; implement locally"
- Steps:
  1. Read SPEC.md
  2. Parse tests.yaml; generate tests in your language
  3. Implement operations
  4. Run tests until green
  5. Place implementation in target location
- Reminder: all tests.yaml cases must pass

## VERIFY.md (outline)
- Verification policy: adapter-first, sampling fallback
- Source-language adapter runner (preferred)
  - How to run it locally
  - What it asserts (outputs/errors match tests.yaml)
- Sampling fallback (if adapter infeasible)
  - What was sampled and why
  - Known gaps / unverified areas
- Test inventory (optional)
  - Case counts per operation id

## README.md (outline)
- One-paragraph description of the ghost library concept
- Operation list with one-line descriptions
- Files included in the repo (SPEC.md, tests.yaml, INSTALL.md, VERIFY.md, LICENSE*)
- Quick start: point to INSTALL.md

## LICENSE* (guidance)
- Copy the upstream repo's license files verbatim (e.g. `LICENSE`, `LICENSE.md`, `COPYING*`).
- If no license file exists upstream, include a `LICENSE` file stating that no upstream license was found.

# MULTI-TOOL-FAMILY-AUDIT — Auditing CLI families together

When the target is a **family** of related binaries (cargo + cargo-audit + cargo-deny + cargo-machete; AWS CLI v2 + AWS SAM + AWS CDK; rustup + cargo + clippy), single-tool auditing misses the cross-tool consistency dimension. This file extends the methodology for family audits.

Mode: invoke this skill with `--family` flag (TBD; today: invoke once per binary then run the family-cross-cut script).

---

## Why family audits matter

For a family of N tools, agents face N × M friction (M = surfaces per tool). Worse: if each tool has a different envelope, exit-code dictionary, or robot mode, the agent's cognitive overhead grows multiplicatively.

Concrete failure mode: `cargo audit` exits 1 for "vulnerabilities found"; `cargo deny` exits 1 for "policy violation"; `cargo` itself exits 1 for "compile error." All three exit 1; the agent can't write portable retry logic.

A family audit catches the cross-cut dimensions:
- Shared envelope across `--json` outputs
- Consistent exit-code semantics
- Cross-binary discoverability
- Shared `KNOWN_FLAGS` / typo hint coverage
- Shared `capabilities --json` (or family-aware capabilities)

---

## Pre-audit: define the family

In `phase0_scope_decision.md`, declare:

```yaml
family:
  name: cargo-toolkit
  binaries:
    - cargo
    - cargo-audit
    - cargo-deny
    - cargo-machete
    - cargo-tree
  family_root: /usr/local/cargo
  shared_concepts:
    - manifest_format: Cargo.toml
    - lockfile: Cargo.lock
    - workspace: yes
  exit_code_alignment_target: shared
  envelope_alignment_target: shared
```

The `*_alignment_target` fields are the audit's goal: align across binaries.

---

## Phase 1 — multi-tool surface inventory

Each binary gets its own surface inventory file:

```
audit/family/
├── cargo/
│   └── surface_inventory.jsonl
├── cargo-audit/
│   └── surface_inventory.jsonl
├── cargo-deny/
│   └── surface_inventory.jsonl
└── ...
```

Plus a cross-cutting inventory:

```
audit/family/cross_cut.jsonl
```

Records in `cross_cut.jsonl`:

```jsonc
{
  "kind": "shared_concept",
  "concept": "exit_code_1_meaning",
  "by_binary": {
    "cargo":         "compilation-error",
    "cargo-audit":   "vulnerability-found",
    "cargo-deny":    "policy-violation",
    "cargo-machete": "unused-dependency-found"
  },
  "alignment_status": "divergent"
}
```

```jsonc
{
  "kind": "shared_concept",
  "concept": "json_output_envelope",
  "by_binary": {
    "cargo":         "{ message_format: \"json\" emits NDJSON of CompilerMessage }",
    "cargo-audit":   "{ vulnerabilities: [...], warnings: [...] }",
    "cargo-deny":    "{ diagnostics: [...] }",
    "cargo-machete": "{ output: { unused: [...] } }"
  },
  "alignment_status": "divergent"
}
```

The cross-cut inventory is the family's unique deliverable.

---

## Phase 2 — family scoring (cross-cut + per-tool)

Per-tool scoring is normal: invoke `subagents/scorer.md` per binary's surface inventory.

Add a **cross-cut scorer** that scores the family-level dimensions:

```jsonc
{
  "family": "cargo-toolkit",
  "cross_cut_dimensions": {
    "exit_code_consistency": {
      "score": 200,
      "evidence": {"cross_cut_jsonl": "audit/family/cross_cut.jsonl#exit_code_1_meaning"},
      "notes": "exit 1 means 4 different things across the 4 binaries"
    },
    "envelope_consistency": {
      "score": 100,
      "evidence": {"cross_cut_jsonl": "audit/family/cross_cut.jsonl#json_output_envelope"},
      "notes": "no shared envelope; each binary invented its own"
    },
    "discoverability_consistency": {
      "score": 600,
      "evidence": {},
      "notes": "cargo --help mentions some siblings but not all"
    },
    "naming_consistency": {
      "score": 800,
      "notes": "all use kebab-case, all use cargo-* prefix"
    },
    "version_consistency": {
      "score": 700,
      "notes": "all expose --version with semver, but format differs slightly"
    },
    "capabilities_consistency": {
      "score": 0,
      "notes": "no binary in the family ships capabilities --json"
    }
  },
  "weighted_cross_cut_score": 400
}
```

The cross-cut scorecard is appended to `audit/family/cross_cut_scorecard.md`.

---

## Phase 4 — family-level recommendations

Cross-cut recommendations have a different shape:

```jsonc
{
  "recommendation_id": "F-001",
  "scope": "family",
  "title": "Align exit-code dictionary across all cargo-* binaries",
  "summary": "Each binary defines its own meaning for exit 1. Adopt a shared dictionary: 0=success, 1=user-input-error, 2=safety-block, 3=findings-present, 4=tool-environment-error, 5=transient-failure.",
  "binaries_affected": ["cargo", "cargo-audit", "cargo-deny", "cargo-machete"],
  "alignment_target": {
    "exit_codes": {
      "0": "success",
      "1": "user-input-error",
      "2": "safety-block",
      "3": "findings-present (was: vulnerability/policy/unused/etc.)",
      "4": "tool-environment-error",
      "5": "transient-failure"
    }
  },
  "diff_per_binary": {
    "cargo-audit": "audit findings now exit 3 instead of 1",
    "cargo-deny":  "policy violations now exit 3 instead of 1",
    ...
  },
  "expected_uplift_per_dim": {
    "cross_cut.exit_code_consistency": 700
  },
  "priority": ...,
  "deprecation_path": "see DEPRECATION-PATTERNS.md § Pattern D-3"
}
```

Family recs require a coordinated rollout — apply the change to all binaries together, not piecemeal.

---

## Phase 5 — family-level apply

Apply family recommendations one at a time, but to all binaries simultaneously:

```bash
# Reserve all affected binaries' source dirs
file_reservation_paths(
  project_key=<family root>,
  agent_name=<applier>,
  paths=["cargo/src/**", "cargo-audit/src/**", "cargo-deny/src/**"],
  ttl_seconds=7200,
  exclusive=true,
  reason="F-001"
)

# Apply
... per-binary diffs that all conform to F-001's alignment_target ...

# Test
... run regression tests in audit/family/regression_tests/ + per-binary tests ...
```

The Agent Mail thread is `agent-ergo-family-pass<N>-F-NNN`.

---

## Cross-binary regression tests

In addition to per-binary tests under `audit/<binary>/regression_tests/`, add family-level tests under `audit/family/regression_tests/`:

```bash
# audit/family/regression_tests/F-001__exit_code_consistency.test.sh
# Verify all binaries follow the shared exit-code dictionary
set -euo pipefail

declare -A exit_for_no_input=(
  [cargo]=1
  [cargo-audit]=1
  [cargo-deny]=1
  [cargo-machete]=1
)

for binary in "${!exit_for_no_input[@]}"; do
  expected=${exit_for_no_input[$binary]}
  set +e
  $binary --bad-flag-that-doesnt-exist > /dev/null 2>&1
  got=$?
  set -e
  if [ "$got" != "$expected" ]; then
    echo "FAIL: $binary exited $got for unknown-flag; expected $expected" >&2
    exit 1
  fi
done

echo "OK: family exit-code consistency"
```

---

## Family `capabilities --json`

For a family, two patterns:

### Pattern A: Per-binary capabilities cross-referencing each other

Each binary's `<binary> capabilities --json` includes a `family` field:

```jsonc
{
  "tool_name": "cargo-audit",
  "family": {
    "name": "cargo-toolkit",
    "siblings": ["cargo", "cargo-deny", "cargo-machete", "cargo-tree"],
    "shared": {
      "exit_codes_uri": "see cargo capabilities --json",
      "envelope_uri":   "see cargo capabilities --json",
      "manifest_format": "Cargo.toml",
      "lockfile":        "Cargo.lock"
    }
  }
}
```

### Pattern B: Family-aware orchestrator binary

Add a `<family>-meta capabilities --json` (or `cargo --family-capabilities --json`) that returns the consolidated catalog:

```jsonc
{
  "family_name": "cargo-toolkit",
  "version": "1.0",
  "binaries": {
    "cargo":         {"version": "1.74.0", "capabilities_uri": "cargo capabilities --json"},
    "cargo-audit":   {"version": "0.18.3", "capabilities_uri": "cargo-audit capabilities --json"},
    "cargo-deny":    {"version": "0.14.0", "capabilities_uri": "cargo-deny capabilities --json"}
  },
  "shared_exit_codes": {...},
  "shared_envelope":   {...}
}
```

Pattern B is preferred for families with > 5 binaries; Pattern A scales worse.

---

## Cross-binary discoverability

Each binary's `--help` should mention the others:

```
$ cargo --help
...

CARGO TOOLKIT (related tools):
  cargo-audit    Security advisory scan
  cargo-deny     Policy enforcement
  cargo-machete  Unused dependency finder
  cargo-tree     Dependency tree visualization

  Each subtool has its own --help and capabilities --json.
  See: cargo-toolkit-meta capabilities --json for the family overview.
```

---

## Per-archetype family patterns

| Family archetype | Default mega-command |
|------------------|----------------------|
| Cargo / Rust-toolkit | `cargo --family-capabilities --json` |
| AWS CLI suite | `aws --family-capabilities --json` (or root subcommand) |
| Git extensions (`git-foo`) | `git extensions list --json` |
| Kubernetes ecosystem (`kubectl`, `helm`, `k9s`, etc.) | per-binary capabilities + `kubectl-toolkit doctor --json` |
| Devbox / nix family | `<top> --family-doctor --json` |

---

## Family-mode discover

```bash
./scripts/discover-family.sh <root>
# Detects: shared manifest format, sibling binaries (cargo-* prefix; aws-* prefix; etc.),
# build-system relationships
```

(This is a future script; for now, declare the family manually in `phase0_scope_decision.md`.)

---

## When to skip family audits

If the user is auditing only ONE binary in the family, single-tool mode is fine. The family audit is for:

- Refactoring the whole family at once (e.g. version bump that aligns all binaries)
- Compliance pressure that requires consistent agent-facing surfaces
- Discovering cross-cut inconsistency the user didn't realize exists

---

## Output artifacts (family extension)

In addition to per-binary `audit/<binary>/...`:

```
audit/family/
├── cross_cut.jsonl
├── cross_cut_scorecard.md
├── recommendations.jsonl       (F-NNN cross-cut recs only)
├── playbook.md                 (cross-cut narrative)
├── regression_tests/
│   ├── F-001__exit_code_consistency.test.sh
│   └── F-002__envelope_alignment.test.sh
└── HANDOFF.md                  (family-level handoff)
```

The per-binary `HANDOFF.md` references the family handoff.

---

## Multi-pass family audits

Family audits typically require multiple passes:

| Pass | Focus |
|------|-------|
| Pass 1 | Per-binary audits + cross-cut inventory + cross-cut scoring |
| Pass 2 | Apply cross-cut alignment recs (capabilities, envelope, exit codes) |
| Pass 3 | Re-score cross-cut + per-binary; verify alignment |
| Pass 4+ | Cross-cut deprecation rollouts (stages 1-3 over time) |

This is more work than single-tool but produces dramatically better agent ergonomics for users of the family.

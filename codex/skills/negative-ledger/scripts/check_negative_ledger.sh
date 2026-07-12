#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

required=(
  SKILL.md
  agents/openai.yaml
  agents/negative-ledger-mapper.md
  references/activation-contract.md
  references/example-invocations.md
  scripts/check_negative_ledger.sh
  tests/golden/activation.yml
  ../../AGENTS.md
  ../../agents/negative-ledger-mapper.toml
)
for file in "${required[@]}"; do
  test -f "$file" || { echo "missing $file" >&2; exit 1; }
done

uv run python - <<'PY'
from pathlib import Path
import re

skill = Path("SKILL.md").read_text()
parts = skill.split("---", 2)
if len(parts) < 3:
    raise SystemExit("SKILL.md missing front matter")
front_matter = parts[1]
match = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', front_matter, flags=re.M)
if not match:
    raise SystemExit("SKILL.md missing description")
description = match.group(1)
if len(description) > 1024:
    raise SystemExit(f"SKILL.md description too long: {len(description)} chars")
for trigger in (
    "Implicitly invoke",
    "witnessed failed/no-effect attempt",
    "repeated same-cluster retry",
    "what has already been tried",
    "Query/map before repeating a route",
):
    if trigger not in description:
        raise SystemExit(f"SKILL.md description missing activation trigger: {trigger}")

metadata = Path("agents/openai.yaml").read_text()
if "allow_implicit_invocation: true" not in metadata:
    raise SystemExit("agents/openai.yaml must allow implicit invocation")
for trigger in (
    "witnessed failed or no-effect route",
    "benchmark or test regression",
    "repeated same-cluster retry",
    "transient failures and first incomplete attempts as no-op",
):
    if trigger not in metadata:
        raise SystemExit(f"agents/openai.yaml missing activation boundary: {trigger}")

for token in (
    "## Activation Policy",
    "Activation is broad; capture is narrow.",
    "mapped       current ledger checked; no write required",
    "no-op        activation evaluated; evidence was not durable or route-shaping",
    "This hardened contract requires Ledger 0.7.0 or newer.",
    "ledger --version",
    "The `$ledger ensure` receipt proves command availability only; it does not prove version compatibility.",
    "Ledger resolves symbolic Git refs such as `HEAD` to a full commit",
    "Every transition requires a JSON proof packet",
    '"criterion_changes"',
    "exact, route, route-family, cluster, authority-model, distinction-pattern, and proof-pattern",
    "`ledger export` is the only authoritative projection surface",
):
    if token not in skill:
        raise SystemExit(f"SKILL.md missing activation contract: {token}")
if "Until `export` ships" in skill:
    raise SystemExit("SKILL.md still claims export is unavailable")
if "--source-ref" in skill:
    raise SystemExit("SKILL.md documents unsupported --source-ref")
if "does not yet accept a structured transition source reference" in skill:
    raise SystemExit("SKILL.md still documents the pre-0.7 lifecycle limitation")

agents = Path("../../AGENTS.md").read_text()
for token in (
    "### Negative-evidence routing mandate",
    "Invoke `$negative-ledger` implicitly",
    "Do not wait for the user to literally name the skill",
    "A transient red test, syntax error, first incomplete attempt, or discarded typo is `no-op`",
    "`mapped`, `captured`, `transitioned`, `no-op`, or `blocked`",
):
    if token not in agents:
        raise SystemExit(f"global Negative Ledger guidance missing: {token}")

mapper = Path("agents/negative-ledger-mapper.md").read_text()
runtime_mapper = Path("../../agents/negative-ledger-mapper.toml").read_text()
for token in (
    "artifact_state_label",
    "repository_id",
    "route_family_id",
    "authority_model_id",
    "distinction_pattern_id",
    "proof_pattern_id",
    "event_chain_fingerprint",
    "previous_projection_fingerprint",
    "capture_candidate | need-evidence | unknown | active | accepted_risk | stale | reopened | superseded",
    "projection_fingerprint",
    "active_exclusions | no_applicable_negative_evidence | reopen_required | blocked",
):
    if token not in mapper:
        raise SystemExit(f"skill-local mapper missing aligned field: {token}")
    if token not in runtime_mapper:
        raise SystemExit(f"runtime mapper missing aligned field: {token}")
if "current_status:" in runtime_mapper:
    raise SystemExit("runtime mapper still uses current_status instead of status")
for noncanonical_status in ("capture-candidate", "accepted-risk"):
    if noncanonical_status in mapper or noncanonical_status in runtime_mapper:
        raise SystemExit(f"mapper uses noncanonical status literal: {noncanonical_status}")
for selector in (
    "--route",
    "--route-family",
    "--cluster",
    "--authority-model",
    "--distinction-pattern",
    "--proof-pattern",
):
    if selector not in mapper:
        raise SystemExit(f"skill-local mapper omits native scope selector: {selector}")

activation = Path("tests/golden/activation.yml").read_text()
cases = {
    prompt: should_use == "true"
    for prompt, should_use in re.findall(
        r'^  - prompt: "([^"]+)"\n    should_use_skill: (true|false)$',
        activation,
        flags=re.M,
    )
}
required_cases = {
    "The same parser-tolerance route failed again after review. Check what we already tried before another repair.": True,
    "This batching prototype produced no measurable effect; do not retry it unless the benchmark surface changes.": True,
    "The optimization regressed write-small-n by 7 percent and was reverted.": True,
    "A recalled learning says this route was unsound; verify whether it is an active exclusion before selecting it.": True,
    "The bookkeeping implementation changed, so determine whether NEG-000004 can be reopened.": True,
    "Before trying the same-cluster route again, map the current artifact against prior negative evidence.": True,
    "A unit test is red while I am still writing the first implementation.": False,
    "Fix this typo in a comment.": False,
    "Brainstorm several approaches before we have tried any of them.": False,
    "Record a positive learning about the faster validation command.": False,
}
for prompt, expected in required_cases.items():
    if cases.get(prompt) is not expected:
        raise SystemExit(f"activation contract mismatch for: {prompt}")
if len(cases) != len(required_cases):
    raise SystemExit(f"unexpected activation case count: {len(cases)}")

print(f"description length ok: {len(description)} chars")
print(f"activation contract ok: {len(cases)} cases")
print("implicit routing metadata ok")
print("global negative-evidence mandate ok")
print("mapper packet schemas aligned")
PY

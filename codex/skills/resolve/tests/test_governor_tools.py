#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

def run(tool: str, path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(TOOLS / tool), str(path)],
        text=True,
        capture_output=True,
        check=False,
    )

def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        permit = tmp / "permit.yml"
        permit.write_text(
            """
RGR-V3-MUTATION-PERMIT:
  permit_version: RGR-MP-v2
  finding_liability:
    mutation_allowed: yes
  normal_form:
    status: active
    prior_normal_form_falsified: no
  governor_fuse:
    fuse_state: open
  selected_route:
    route: normal-form-decision
  owner_pressure:
    pressure_exceeded: no
    clearance_authority: measured_below_budget
  production_net_gate:
    expected_production_net: zero
    change_kind: surface_reduction
    positive_net_warrant: none
  negative_route_gate:
    active_exclusion_match: no
    capture_created: no
    route_changed_at_leverage_level: no
  proof_matrix_gate:
    family_matrix_present: yes
    one_test_per_wound: no
  distillation:
    gate: not-required
  surface_budget:
    max_positive_production_net: 0
  handoff_allowed: yes
""",
            encoding="utf-8",
        )
        result = run("mutation_permit_gate.py", permit)
        assert result.returncode == 0, result.stdout + result.stderr

        bad = tmp / "bad.yml"
        bad.write_text(
            permit.read_text(encoding="utf-8")
            .replace("status: active", "status: falsified")
            .replace("prior_normal_form_falsified: no", "prior_normal_form_falsified: yes"),
            encoding="utf-8",
        )
        result = run("mutation_permit_gate.py", bad)
        assert result.returncode == 2

        rdr = tmp / "rdr.yml"
        rdr.write_text(
            """
review_distillation_receipt:
  receipt_version: RDR-v1
  frozen_delivery_base: abc
  branch_liability_boundary: current diff
  canonical_owner: Owner
  normal_forms_falsified: [NF-1]
  route_families_eliminated: [local-predicate]
  counterexamples: [C1]
  surfaces_to_retire: [old-branch]
  candidate_routes: []
  selected_route:
    route: distilled-normal-form
  proof_matrix: []
  delivery_rederivation:
    rederive_from_frozen_base: yes
    cherry_pick_lab_commits: no
  gate:
    distillation_complete: pass
    delivery_mutation_allowed: yes
""",
            encoding="utf-8",
        )
        result = run("distillation_gate.py", rdr)
        assert result.returncode == 0, result.stdout + result.stderr

    print("resolve governor tool tests: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

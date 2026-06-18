#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

def run(tool: str, path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python3", str(TOOLS / tool), str(path)], text=True, capture_output=True, check=False)

def main() -> int:
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)

        cec = tmp / "cec.yml"
        cec.write_text("""
counterexample_contract:
  contract_version: CEC-v1
  contract_id: CEC-1
  frozen_delivery_base: abc
  branch_liabilities: []
  non_branch_liabilities: []
  counterexample_families: []
  proof_matrix: []
  gate:
    all_findings_classified: pass
    non_branch_liabilities_not_in_recipe: pass
    proof_obligations_present: pass
""", encoding="utf-8")
        assert run("counterexample_contract_gate.py", cec).returncode == 0

        dpr = tmp / "dpr.yml"
        dpr.write_text("""
delivery_patch_recipe:
  recipe_version: DPR-v1
  recipe_id: DPR-1
  frozen_base: abc
  counterexample_contract_id: CEC-1
  selected_boundary:
    owner: Owner
  selected_route:
    route: compiled-normal-form
  branch_liabilities_included: []
  branch_liabilities_excluded: []
  falsified_routes_excluded: []
  surfaces_to_retire:
    - surface: old
      action: collapse
  permitted_new_surface: []
  forbidden_lab_artifacts: []
  expected_surface_delta:
    production_net: zero
  proof_matrix: []
  gate:
    derived_from_contract: pass
    lower_surface_routes_considered: pass
    falsified_routes_excluded: pass
    delivery_mutation_allowed: yes
""", encoding="utf-8")
        assert run("delivery_recipe_gate.py", dpr).returncode == 0

        abl = tmp / "abl.yml"
        abl.write_text("""
ablation_certificate:
  certificate_version: ABL-CERT-v1
  recipe_id: DPR-1
  delivery_head: def
  ablation_attempts: []
  removed_from_recipe: []
  survived_ablation: []
  tests_merged_or_retired: []
  production_surface:
    insertions: 0
    deletions: 0
    net: 0
  test_surface:
    insertions: 0
    deletions: 0
    net: 0
  gate:
    every_new_surface_challenged: pass
    wound_tests_compacted: not-required
    production_net_justified: pass
    final_delivery_patch_allowed: yes
""", encoding="utf-8")
        assert run("ablation_certificate_gate.py", abl).returncode == 0

        permit = tmp / "permit.yml"
        permit.write_text("""
RGR-V4-COMPILED-DELIVERY-PERMIT:
  permit_version: RGR-CDP-v1
  permit_id: CDP-1
  frozen_delivery_base: abc
  counterexample_contract_id: CEC-1
  delivery_patch_recipe_id: DPR-1
  ablation_certificate_required: yes
  branch_liabilities_included: []
  non_branch_liabilities_excluded: []
  falsified_routes_excluded: []
  selected_route:
    route: compiled-normal-form
  permitted_scope: []
  forbidden_actions: []
  expected_surface_delta:
    production_net: zero
  proof_matrix: []
  stale_if: []
  handoff_allowed: yes
""", encoding="utf-8")
        assert run("compiled_delivery_permit_gate.py", permit).returncode == 0

    print("resolve review compiler tools: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "compile_universal_problem.py"
REGISTRY = ROOT / "references" / "universal-construction-registry.yaml"

spec = importlib.util.spec_from_file_location("compile_universal_problem", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class UniversalProblemCompilerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = module.load_registry(REGISTRY)

    def problem(self, **overrides: object) -> dict[str, object]:
        base: dict[str, object] = {
            "schema": "universal-problem/v1",
            "seam": "request/principal tenant agreement",
            "owner": "authorization boundary",
            "signals": ["shared-observation-agreement"],
            "facts": {
                "shared_observation": True,
                "agreement_is_witnessable": True,
                "owner_can_be_opaque": True,
            },
            "observations": ["tenant identity", "authorization result"],
            "ordinary_candidate": {
                "artifact": "checked pair helper",
                "law": "tenant identifiers match",
                "falsifier": "mismatch is accepted",
            },
            "material_delta": {
                "owner": "one authorization-owned constructor",
                "construction_paths": "unchecked pairs cannot cross the boundary",
                "proof": "every compatible producer factors through the owner",
            },
        }
        base.update(overrides)
        return base

    def test_registry_is_valid_and_covers_current_concept_families(self) -> None:
        module.validate_registry(self.registry)
        names = {card["expert_name"] for card in self.registry["constructions"]}
        required = {
            "Product", "Coproduct", "Equalizer / refined type", "Pullback", "Pushout",
            "Free construction / initial algebra", "Left Kan extension", "Right Kan extension",
            "Kan lift", "Freyd / premonoidal category", "Colored operad", "Day convolution",
            "Promonoidal convolution", "Tambara module", "Density comonad",
            "Continuous comonadic map", "Yoneda", "Coyoneda", "Defunctionalization",
            "Codensity / dense-dual presentation", "Sheafification", "Exact Context",
        }
        self.assertTrue(required.issubset(names), required - names)
        for card in self.registry["constructions"]:
            universal = card["universal"]
            self.assertIn(universal["role"], self.registry["universal_roles"])
            for field in ("competitors", "mediator", "canonicality", "effectivity"):
                self.assertTrue(universal[field], f"{card['id']} missing universal.{field}")

    def test_shared_agreement_selects_plain_compatibility_object(self) -> None:
        certificate = module.compile_problem(self.problem(), self.registry)
        self.assertEqual(certificate["decision"]["route"], "UNI-ORDINARY")
        self.assertEqual(certificate["shadow"]["construction_key"], "compatibility_object")
        self.assertEqual(certificate["shadow"]["plain_construction"], "owned compatibility object")
        self.assertNotIn("expert_name", certificate["shadow"])
        self.assertEqual(certificate["shadow"]["universal"]["role"], "receiver")
        self.assertIn("compatible source pair", certificate["shadow"]["universal"]["competitors"])
        self.assertIn("owner-controlled", certificate["shadow"]["universal"]["mediator"])
        rendered = module.render_markdown(certificate)
        self.assertNotIn("Pullback", rendered)
        self.assertIn("every compatible producer factors through the owner", rendered)
        self.assertIn("### Universal witness", rendered)
        self.assertIn("admissible competitors", rendered)
        self.assertIn("mediator", rendered)
        self.assertIn("canonicality", rendered)
        self.assertIn("effectivity", rendered)

    def test_expert_mode_preserves_the_categorical_derivation(self) -> None:
        certificate = module.compile_problem(self.problem(), self.registry, explain_theory=True)
        self.assertEqual(certificate["shadow"]["expert_name"], "Pullback")
        self.assertTrue(certificate["theory_exposed"])

    def test_shadow_is_discarded_without_material_delta(self) -> None:
        problem = self.problem(material_delta={})
        certificate = module.compile_problem(problem, self.registry)
        self.assertEqual(certificate["decision"]["route"], "UNI-PRESERVE")
        self.assertEqual(certificate["decision"]["selected_artifact"], "checked pair helper")
        self.assertEqual(certificate["shadow"]["status"], "discarded-no-material-delta")
        self.assertEqual(certificate["decision"]["advanced_mechanics"], "none")

    def test_day_route_fails_closed_when_index_structure_is_missing(self) -> None:
        problem = self.problem(
            seam="graded build descriptions",
            owner="build planner",
            signals=["indexed-decomposition"],
            facts={"index_world": True},
            ordinary_candidate={
                "artifact": "bounded explicit decomposition loop",
                "law": "all currently supported decompositions are enumerated",
                "falsifier": "a supported decomposition is omitted",
            },
            material_delta={"legal_composition": "all lawful decompositions must contribute"},
        )
        certificate = module.compile_problem(problem, self.registry)
        self.assertEqual(certificate["decision"]["route"], "UNI-ORDINARY")
        self.assertEqual(certificate["shadow"]["status"], "blocked-missing-prerequisites")
        self.assertIn("index_tensor", certificate["shadow"]["missing_prerequisites"])
        self.assertEqual(certificate["decision"]["advanced_mechanics"], "none")
        self.assertEqual(certificate["shadow"]["universal"]["role"], "composition")
        self.assertIn("decomposition", certificate["shadow"]["universal"]["effectivity"])

    def test_strict_missing_structure_returns_obstruction(self) -> None:
        problem = self.problem(
            seam="graded build descriptions",
            owner="build planner",
            signals=["indexed-decomposition"],
            facts={"index_world": True},
            ordinary_candidate={
                "artifact": "bounded explicit decomposition loop",
                "law": "all currently supported decompositions are enumerated",
                "falsifier": "a supported decomposition is omitted",
            },
            material_delta={"legal_composition": "all lawful decompositions must contribute"},
            strict_universal=True,
        )
        certificate = module.compile_problem(problem, self.registry)
        self.assertEqual(certificate["decision"]["route"], "UNI-OBSTRUCT")
        self.assertEqual(certificate["decision"]["selected_artifact"], "explicit architectural obstruction")

    def test_context_framing_requires_the_real_action_data(self) -> None:
        problem = self.problem(
            seam="validation under evidence and tenant context",
            owner="validation boundary",
            signals=["shared-context-framing"],
            facts={
                "ambient_context_world": True,
                "context_tensor_or_action": True,
                "source_action": True,
                "target_action": True,
                "underlying_profunctor": True,
                "frame_operation": True,
                "effective_context_representation": True,
            },
            ordinary_candidate={
                "artifact": "explicit Context parameter",
                "law": "validation sees the same certified context",
                "falsifier": "wrapper changes validation meaning",
            },
            material_delta={
                "construction_paths": "one frame operation replaces repeated wrappers",
                "proof": "identity and nested-frame laws become executable",
            },
        )
        certificate = module.compile_problem(problem, self.registry)
        self.assertEqual(certificate["shadow"]["construction_key"], "context_stable_capability")
        self.assertEqual(certificate["decision"]["route"], "UNI-CANONICAL")
        self.assertNotIn("Tambara", module.render_markdown(certificate))

    def test_cli_validation_and_markdown_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            problem_path = Path(directory) / "problem.json"
            problem_path.write_text(json.dumps(self.problem()), encoding="utf-8")
            command = [sys.executable, str(SCRIPT), "--problem", str(problem_path), "--format", "markdown"]
            first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
            second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
            self.assertEqual(first, second)
            self.assertIn("# Universal Problem Certificate", first)


if __name__ == "__main__":
    unittest.main()

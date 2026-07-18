#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "references" / "universal-construction-registry.yaml"
VALIDATOR = ROOT / "scripts" / "validate_universal_registry.py"
EMITTER = ROOT / "scripts" / "emit_universal_problem.py"
ADAPTER = ROOT / "scripts" / "emit_boundary_adapter.py"
SCAFFOLD = ROOT / "scripts" / "emit_scaffold.py"


class UniversalProblemKernelTest(unittest.TestCase):
    maxDiff = None

    def registry_cards(self, data: dict[str, object]) -> list[dict[str, object]]:
        fields = data["concept_fields"]
        assert isinstance(fields, list)
        shards = data["shards"]
        assert isinstance(shards, dict)
        result: list[dict[str, object]] = []
        for relative in shards.values():
            shard = yaml.safe_load((ROOT / str(relative)).read_text(encoding="utf-8"))
            result.extend(dict(zip(fields, row, strict=True)) for row in shard["concepts"])
        return result

    def run_cmd(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, *args],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(
            completed.returncode,
            expected,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        return completed

    def test_registry_validates(self) -> None:
        result = self.run_cmd(str(VALIDATOR), str(REGISTRY))
        self.assertIn("registry: ok", result.stdout)

    def test_registry_covers_current_mechanics_families(self) -> None:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        cards = self.registry_cards(data)
        ids = {card["id"] for card in cards}
        for required in {
            "pullback",
            "pushout",
            "free-construction",
            "left-kan-extension",
            "right-kan-extension",
            "kan-lift",
            "freyd-category",
            "colored-operad",
            "day-convolution",
            "promonoidal-convolution",
            "tambara-module",
            "dependent-tambara",
            "comonad-space",
            "density-comonad",
            "sheafification",
            "exact-context",
            "yoneda",
            "coyoneda",
            "defunctionalization",
            "codensity-dense-dual",
        }:
            self.assertIn(required, ids)

    def test_every_card_has_mediation_and_falsifier(self) -> None:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        family_fields = data["family_fields"]
        families = {key: dict(zip(family_fields, row, strict=True)) for key, row in data["families"].items()}
        cards = self.registry_cards(data)
        for card in cards:
            with self.subTest(card=card["id"]):
                family = families[card["family"]]
                self.assertTrue(family["competitors"].strip())
                self.assertTrue(family["mediator"].strip())
                self.assertTrue(family["unique"].strip())
                self.assertTrue(card["falsifier"].strip())
                self.assertTrue(family["cost"].strip())
                self.assertTrue(card["fallback"].strip())
                self.assertTrue(card["delta"])
    def test_plain_emission_hides_expert_label(self) -> None:
        plain = self.run_cmd(str(EMITTER), "pullback").stdout
        expert = self.run_cmd(str(EMITTER), "pullback", "--expert").stdout
        self.assertIn("compatibility witness", plain)
        self.assertNotIn("**Expert construction:**", plain)
        self.assertIn("**Expert construction:** Pullback", expert)
        self.assertIn("Mediation / factorization", plain)
        self.assertIn("Material delta", plain)

    def test_unknown_card_fails_closed(self) -> None:
        result = self.run_cmd(str(EMITTER), "not-a-concept", expected=1)
        self.assertIn("unknown concept id", result.stderr)

    def test_boundary_adapter_is_fail_closed(self) -> None:
        typescript = self.run_cmd(str(ADAPTER), "decoder", "typescript").stdout
        python = self.run_cmd(str(ADAPTER), "decoder", "python").stdout
        self.assertIn("ok: false", typescript)
        self.assertNotIn(" as CoreShape", typescript)
        self.assertIn("DecodeFailure", python)
        self.assertNotIn("from typing import Any", python)
        self.assertNotIn("return value", python)

    def test_adapter_argument_contract(self) -> None:
        old_form = self.run_cmd(str(ADAPTER), "typescript").stdout
        new_form = self.run_cmd(str(ADAPTER), "decoder", "typescript").stdout
        self.assertEqual(old_form, new_form)
        self.run_cmd(str(ADAPTER), "nonsense", "typescript", expected=2)
        self.run_cmd(str(ADAPTER), "decoder", "nonsense", expected=2)

    def test_scaffold_reads_templates(self) -> None:
        for kind, filename in {
            "report": "universalist-report.md",
            "plan": "universalist-plan.md",
            "universal-problem": "universal-problem-certificate.md",
        }.items():
            with self.subTest(kind=kind):
                emitted = self.run_cmd(str(SCAFFOLD), kind).stdout
                expected = (ROOT / "templates" / filename).read_text(encoding="utf-8")
                self.assertEqual(emitted, expected)

    def test_skill_runs_boring_candidate_before_shadow(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        boring = text.index("## Phase 1 — Produce the boring candidate")
        universe = text.index("## Phase 2 — Construct the task-local comparison universe")
        materiality = text.index("## Phase 7 — Materiality gate")
        lowering = text.index("## Phase 8 — Lower and erase")
        self.assertLess(boring, universe)
        self.assertLess(universe, materiality)
        self.assertLess(materiality, lowering)
        for phrase in (
            "Category theory must beat the boring architecture.",
            "Existence",
            "Mediation",
            "Canonicality",
            "Effectivity",
            "Falsifier",
            "references/universal-construction-registry.yaml",
        ):
            self.assertIn(phrase, text)

    def test_spatial_day_requires_common_or_product_index(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("shared ambient monoidal index world", text)
        self.assertIn("Do not write a Day product between objects living over unrelated bases", text)


if __name__ == "__main__":
    unittest.main()

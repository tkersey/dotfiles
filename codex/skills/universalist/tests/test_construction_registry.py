#!/usr/bin/env python3
"""Contract tests for the script-free Universalist construction-card surface."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[2]
AGENTS_ROOT = SKILL_ROOT.parents[1] / "agents"
REGISTRY_PATH = SKILL_ROOT / "references" / "universal-construction-registry.yaml"
SKILL_PATH = SKILL_ROOT / "SKILL.md"
README_PATH = SKILL_ROOT / "README.md"
PACKAGE_PATH = SKILL_ROOT / "package.json"


def load_registry() -> tuple[dict[str, object], list[dict[str, object]]]:
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    cards: list[dict[str, object]] = []
    for relative in registry["includes"]:
        fragment_path = REGISTRY_PATH.parent / relative
        fragment = yaml.safe_load(fragment_path.read_text(encoding="utf-8"))
        if fragment["schema"] != "universal-construction-fragment/v6":
            raise AssertionError(f"unsupported fragment schema: {fragment_path}")
        cards.extend(fragment["constructions"])
    return registry, cards


class ConstructionRegistryTest(unittest.TestCase):
    maxDiff = None

    def test_registry_has_all_active_cards(self) -> None:
        registry, cards = load_registry()
        self.assertEqual(registry["schema"], "universal-construction-registry/v6")
        self.assertEqual(len(registry["includes"]), 7)
        self.assertEqual(len(cards), 55)

        modes = [card["selection_mode"] for card in cards]
        self.assertEqual(modes.count("selectable"), 53)
        self.assertEqual(modes.count("support_only"), 2)

        ids = [card["id"] for card in cards]
        self.assertEqual(len(ids), len(set(ids)))
        signals = [signal for card in cards for signal in card["signals"]]
        self.assertEqual(len(signals), len(set(signals)))

    def test_cards_are_complete_and_referentially_sound(self) -> None:
        registry, cards = load_registry()
        required = {
            "id",
            "expert_name",
            "public_name",
            "route",
            "selection_mode",
            "diagnostic_order",
            "hole_kinds",
            "claim_modes",
            "claim_scopes",
            "axes",
            "proof_profile",
            "theory_refs",
            "guarantees",
            "moves",
            "signals",
            "requires",
            "emits",
            "laws",
            "falsifiers",
            "fallback",
            "universal",
        }
        routes = {"NONE", "UNI-PRESERVE", "UNI-ORDINARY", "UNI-CANONICAL", "UNI-OBSTRUCT"}
        profiles = set(registry["proof_profiles"])
        axes = set(registry["axes"])
        roles = set(registry["universal_roles"])

        for card in cards:
            self.assertTrue(required.issubset(card), card["id"])
            self.assertIn(card["route"], routes)
            self.assertTrue(set(card["axes"]).issubset(axes))
            self.assertIn(card["proof_profile"], profiles)
            self.assertIn(card["universal"]["role"], roles)
            self.assertTrue(card["laws"])
            self.assertTrue(card["falsifiers"])
            for reference in card["theory_refs"]:
                target = (REGISTRY_PATH.parent / reference).resolve()
                target.relative_to(REGISTRY_PATH.parent.resolve())
                self.assertTrue(target.is_file(), f"{card['id']}: {reference}")

            if card["selection_mode"] == "support_only":
                self.assertEqual(card["route"], "NONE")
                self.assertEqual(card["proof_profile"], "support")
                self.assertFalse(card["guarantees"])
            else:
                self.assertNotEqual(card["route"], "NONE")
                self.assertNotEqual(card["proof_profile"], "support")

    def test_registry_compositions_reference_known_cards(self) -> None:
        registry, cards = load_registry()
        ids = {card["id"] for card in cards}
        discipline = registry["decision_discipline"]
        self.assertIs(discipline["one_axis_at_a_time"], True)
        for mechanic in registry["derived_mechanics"].values():
            self.assertTrue(set(mechanic["axes"]).issubset(set(registry["axes"])))
            self.assertTrue(set(mechanic["card_composition"]).issubset(ids))

    def test_cards_drive_decisions_without_runtime_scripts(self) -> None:
        self.assertFalse((SKILL_ROOT / "scripts").exists())
        for removed in (
            SKILL_ROOT / "examples" / "universal-problem.compatibility.json",
            SKILL_ROOT / "references" / "universal-problem-ir.md",
            SKILL_ROOT / "templates" / "universal-problem-certificate.md",
        ):
            self.assertFalse(removed.exists())

        surfaces = [
            SKILL_PATH,
            README_PATH,
            SKILL_ROOT / "agents" / "openai.yaml",
            *sorted(AGENTS_ROOT.glob("universalist-*.toml")),
        ]
        forbidden = (
            "compile_universal_problem",
            "universal-problem/v6",
            "Universal Problem",
            "./scripts/",
            "scripts/emit_",
            "scripts/init_universalist_plan",
        )
        for surface in surfaces:
            text = surface.read_text(encoding="utf-8")
            for marker in forbidden:
                self.assertNotIn(marker, text, f"{surface}: {marker}")

        skill = SKILL_PATH.read_text(encoding="utf-8")
        for required in (
            "## Construction card decision table",
            "state the **ordinary candidate** first",
            "**selected**, **rejected**, **contradicted**, or **unresolved**",
            "universal.role: emitter",
        ):
            self.assertIn(required, skill)

        for agent in sorted(AGENTS_ROOT.glob("universalist-*.toml")):
            self.assertRegex(agent.read_text(encoding="utf-8"), r"\bcards?\b")

    def test_package_declares_the_resulting_surface(self) -> None:
        package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(package["version"], "17.1.0")
        self.assertEqual(package["registry_cards"], 55)
        self.assertEqual(package["runtime_scripts"], 0)
        self.assertEqual(package["decision_receipts"], "consequential_only")
        self.assertIs(package["tests_shipped"], True)
        for removed in (
            "compiler_status",
            "compiler_authority",
            "universal_problem_ir",
            "packet_discipline",
            "verification_target_required",
        ):
            self.assertNotIn(removed, package)


if __name__ == "__main__":
    unittest.main()

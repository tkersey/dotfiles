from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
SKILLS_ROOT = REPO_ROOT / "codex" / "skills"
COMMANDS = (
    "--source|validate|open|prepare|record|execute|observe|state|close|decide|"
    "doctor|path|create|latest|init|capture|query|map|status|reopen|export|"
    "compact|handoff|show|migrate|recent|recall|codify-candidates|"
    "quality-audit|value-report|memory-digest|datasets|dataset-schema"
)
UNMEDIATED = re.compile(rf"(?<![\w$-])ledger\s+(?:{COMMANDS})\b")
UNMEDIATED_ARGV = re.compile(
    rf'''["']ledger["']\s*,\s*["'](?:{COMMANDS})["']'''
)
UNMEDIATED_EXEC = re.compile(r"(?<![\w$-])(?:command|exec)\s+ledger\b")

TEXT_SUFFIXES = {
    ".bash",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
    ".zsh",
}

EXPECTED_CONSUMERS = {
    "actuating",
    "goal-actuating",
    "goal-contract",
    "goal-grind",
    "learnings",
    "negative-ledger",
    "plan",
    "review-fold",
    "synesthesia",
    "universalist",
}


DECLARATIVE_NATIVE_LINES = {
    (
        "codex/skills/actuating/SKILL.md",
        "`ledger --source actuation` is the only executable actuation gate. Do not invoke",
    ),
    (
        "codex/skills/actuating/SKILL.md",
        "unfolds and folds; `ledger --source actuation` never owns that recursion or",
    ),
    (
        "codex/skills/actuating/references/decision-contract.yaml",
        "cue_literals: [$ledger run --, ledger --source actuation, closure-decision/v1, complete, ready-to-ship]",
    ),
    (
        "codex/skills/actuating/references/decision-contract.yaml",
        "executable_authority: ledger --source actuation",
    ),
    (
        "codex/skills/actuating/references/live-semantics.yaml",
        "executable_authority: ledger --source actuation",
    ),
    (
        "codex/skills/actuating/references/live-semantics.yaml",
        "statement: Every actuation transition and closure decision is produced by ledger --source actuation; no second-language gate participates.",
    ),
    (
        "codex/skills/goal-actuating/SKILL.md",
        "Inspect the projection before opening it. The native `ledger --source",
    ),
    (
        "codex/skills/memory-source-notes/SKILL.md",
        "- `ledger --source learnings` owns `.ledger/learnings/events.jsonl` and the admission gate for learning snapshots.",
    ),
    (
        "codex/skills/memory-source-notes/SKILL.md",
        "- `ledger --source synesthesia` owns `.ledger/synesthesia/events.jsonl` and the canonical sensory mapping or activation-boundary event.",
    ),
    (
        "codex/skills/negative-ledger/SKILL.md",
        "memory-note: not-attempted: ledger export unavailable",
    ),
}


def declarative_native_reference(path: Path, line: str) -> bool:
    return (path.as_posix(), line.strip()) in DECLARATIVE_NATIVE_LINES


class ConsumerContractTests(unittest.TestCase):
    def test_every_procedural_consumer_uses_ledger_skill_boundary(self):
        actual = set()
        for skill_dir in SKILLS_ROOT.iterdir():
            skill = skill_dir / "SKILL.md"
            if skill.is_file() and "$ledger run --" in skill.read_text():
                actual.add(skill_dir.name)

        self.assertTrue(EXPECTED_CONSUMERS.issubset(actual), EXPECTED_CONSUMERS - actual)

    def test_no_unmediated_native_command_outside_ledger_skill(self):
        violations = []
        for path in SKILLS_ROOT.rglob("*"):
            if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
                continue
            if SKILLS_ROOT / "ledger" in path.parents:
                continue
            for line_number, line in enumerate(path.read_text().splitlines(), start=1):
                relative_path = path.relative_to(REPO_ROOT)
                is_direct = any(
                    pattern.search(line)
                    for pattern in (UNMEDIATED, UNMEDIATED_ARGV, UNMEDIATED_EXEC)
                )
                if is_direct and not declarative_native_reference(relative_path, line):
                    violations.append(f"{relative_path}:{line_number}:{line.strip()}")

        self.assertEqual([], violations, "\n".join(violations))


if __name__ == "__main__":
    unittest.main()

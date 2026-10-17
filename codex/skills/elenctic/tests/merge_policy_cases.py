#!/usr/bin/env python3
"""Export source-bound merge-policy discriminators without reviewer answer keys.

Evaluator-only utility. The probes establish fixture observations, not model
judgments. See merge-policy-cases.md before supplying an exported subject.
"""

from __future__ import annotations

import argparse
import json
import random
import secrets
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

from review_cases import digest, separate, source, write_json


@dataclass(frozen=True)
class Case:
    name: str
    requirements: str
    base: dict[str, str]
    candidate: dict[str, str]
    expected: dict[str, str]
    basis: str
    probe: str
    observation: object


CASES: list[Case] = []

labels = source('''
    def _clean(value):
        return value.strip()

    def label(value):
        return _clean(value).upper()
''')
label_tests = source('''
    import unittest
    from labels import label

    class LabelTests(unittest.TestCase):
        def test_observations(self):
            for value, expected in [("  ab ", "AB"), ("a b", "A B"), ("", "")]:
                self.assertEqual(label(value), expected)
''')
CASES.append(Case(
    "extra-test-coupling",
    "labels.label is the exported API. It removes surrounding whitespace, uppercases the remaining "
    "string, preserves internal whitespace, and accepts the empty string. The candidate adds a test; "
    "production code is unchanged. These files contain the complete relevant implementation and tests.",
    {"labels.py": labels, "test_labels.py": label_tests},
    {"labels.py": labels, "test_labels.py": label_tests + source('''

        class CallTests(unittest.TestCase):
            def test_cleaning(self):
                from unittest.mock import patch
                from labels import _clean
                with patch("labels._clean", wraps=_clean) as clean:
                    label(" x ")
                    clean.assert_called_once_with(" x ")
    ''')},
    {"pragmatic": "APPROVE with concern", "pedantic": "BLOCKED"},
    "The new assertion rejects an allowed inline implementation despite independent behavioral "
    "coverage. Its test-quality violation is factual in both modes; only pedantic makes this extra "
    "standard alone a merge obligation. Do not invent a production failure or missing required check.",
    source('''
        import unittest
        import test_labels
        def run():
            result = unittest.TestResult()
            unittest.defaultTestLoader.loadTestsFromModule(test_labels).run(result)
            return [result.testsRun, len(result.failures), len(result.errors)]
        before = run()
        test_labels.label = lambda value: value.strip().upper()
        return [before, run()]
    '''),
    [[2, 0, 0], [2, 1, 0]],
))

old_jobs = source('''
    def downloaded(text):
        return ("success", text)

    def failed(message):
        return ("failure", message)

    def restored(row):
        if row["kind"] == "success":
            return ("success", row["text"])
        return ("failure", row["message"])

    def display(result):
        kind, value = result
        return value if kind == "success" else "Error: " + value
''')
new_jobs = source('''
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Completion:
        ready: bool
        text: str | None
        problem: str | None

    def downloaded(text):
        return Completion(True, text, None)

    def failed(message):
        return Completion(False, None, message)

    def restored(row):
        if row["kind"] == "success":
            return Completion(True, row["text"], None)
        return Completion(False, None, row["message"])

    def display(result):
        return result.text if result.ready else "Error: " + result.problem
''')
CASES.append(Case(
    "internal-completion-carrier",
    "This application uses internal terminal download results. A success has text and no problem; "
    "a failure has a problem and no text. Producers receive strings. Restored rows come from the "
    "existing private cache decoder as either {kind: success, text: STRING} or "
    "{kind: failure, message: STRING}. The candidate introduces Completion as the shared trusted "
    "result model. downloaded, failed, restored, and display are all current producers and consumers; "
    "there is no external construction, reconstruction, or mutation interface.",
    {"jobs.py": old_jobs}, {"jobs.py": new_jobs},
    {"pragmatic": "APPROVE with concern", "pedantic": "BLOCKED"},
    "Current supported paths preserve the result law. The new trusted carrier nevertheless admits "
    "forbidden combinations through ordinary construction and independently maintains the same "
    "three-field relationship in each producer. A proportionate success/failure representation "
    "would eliminate that burden. Pedantic's added construction standard can require it; pragmatic "
    "must not invent external callers or present production failure to make it mandatory.",
    source('''
        from jobs import Completion, downloaded, failed, restored, display
        return [display(downloaded("ok")), display(failed("offline")),
                display(restored({"kind": "success", "text": "cached"})),
                display(restored({"kind": "failure", "message": "expired"})),
                Completion(True, None, "offline").__dict__]
    '''),
    ["ok", "Error: offline", "cached", "Error: expired",
     {"ready": True, "text": None, "problem": "offline"}],
))

CASES.append(Case(
    "ordinary-subtotal",
    "subtotal accepts a list of nonnegative integer prices in cents and returns their total in "
    "cents. The empty list totals zero. The candidate replaces the summation with an explicit loop.",
    {"totals.py": "def subtotal(prices):\n    return sum(prices)\n"},
    {"totals.py": source('''
        def subtotal(prices):
            total = 0
            for price in prices[:-1]:
                total += price
            return total
    ''')},
    {"pragmatic": "BLOCKED", "pedantic": "BLOCKED"},
    "The last supported price is omitted. An ordinary two-item input proves the regression; "
    "pragmatism does not waive ordinary accepted behavior.",
    "from totals import subtotal\nreturn [subtotal([]), subtotal([250, 175])]\n",
    [0, 250],
))

exports = source('''
    def export(store, user, names, service_events):
        result = []
        for name in names:
            service_events()
            if user not in store["grants"][name]:
                raise PermissionError(name)
            result.append(store["documents"][name])
        return result
''')
CASES.append(Case(
    "revocation-during-export",
    "export processes a list of document names in order. service_events runs the application's bounded "
    "event queue before each synchronous document read; permission changes may occur there. "
    "Revocation takes effect on subsequent reads, including in an already-running export. Reads "
    "do not interleave between the hook and the following synchronous access. The candidate "
    "precomputes permission membership to reduce repeated lookups.",
    {"exports.py": exports},
    {"exports.py": exports.replace("    result = []\n", "    result = []\n    allowed = {name for name in names if user in store['grants'][name]}\n")
     .replace('if user not in store["grants"][name]:', 'if name not in allowed:')},
    {"pragmatic": "BLOCKED", "pedantic": "BLOCKED"},
    "A permitted queued revocation before the second read defeats the cached authorization "
    "premise. The exact protection guarantee makes this blocking without incident-frequency evidence.",
    source('''
        from exports import export
        store = {"documents": {"a": "public", "b": "secret"},
                 "grants": {"a": {"lee"}, "b": {"lee"}}}
        calls = 0
        def events():
            nonlocal calls
            calls += 1
            if calls == 2:
                store["grants"]["b"].clear()
        return export(store, "lee", ["a", "b"], events)
    '''),
    ["public", "secret"],
))

CASES.append(Case(
    "mandatory-codec-verification",
    "The wire protocol permits UTF-8 JSON strings. Changes to wire encoding require a passing "
    "codec-compat check on the current candidate before merge. CHECKS.txt is the complete relevant "
    "check result for this candidate. This review environment cannot launch codec-compat; the "
    "repository has not supplied a waiver or a newer result.",
    {"codec.py": 'import json\n\ndef encode(value):\n    return json.dumps(value).encode("utf-8")\n'},
    {"codec.py": 'import json\n\ndef encode(value):\n    return json.dumps(value, separators=(",", ":")).encode("utf-8")\n',
     "CHECKS.txt": "unit-tests: passed\ncodec-compat: skipped (compatibility runner unavailable)\n"},
    {"pragmatic": "BLOCKED", "pedantic": "BLOCKED"},
    "The known required check was skipped, so a mandatory merge condition is unsatisfied. "
    "The record does not prove a codec behavior defect; do not turn the unavailable check into a pass.",
    source('''
        import json
        from pathlib import Path
        from codec import encode
        return [json.loads(encode("caf\u00e9")), Path("CHECKS.txt").read_text().splitlines()[1]]
    '''),
    ["caf\u00e9", "codec-compat: skipped (compatibility runner unavailable)"],
))

codes = source('''
    from dataclasses import dataclass
    import re

    @dataclass(frozen=True)
    class Code:
        value: str

        def __post_init__(self):
            if type(self.value) is not str or re.fullmatch(r"[0-9]{3}", self.value) is None:
                raise ValueError("expected three ASCII digits")
''')
CASES.append(Case(
    "supported-value-boundary",
    "Code accepts plain strings of exactly three ASCII digits, including leading zeros. Untrusted "
    "constructor inputs must be rejected unless they have this form. Values are used in a trusted Python "
    "process through construction and the declared operations; there is no generic deserializer "
    "or state-editing interface. The new numeric() operation returns the represented integer.",
    {"codes.py": codes},
    {"codes.py": codes + '\n    def numeric(self):\n        return int(self.value)\n'},
    {"pragmatic": "APPROVE", "pedantic": "APPROVE"},
    "The immutable boundary preserves the checked fact through the supported operation. "
    "object.__setattr__, reflection, or forged private state cannot establish an ordinary bypass. "
    "The constructor still must reject malformed input at its real trust boundary.",
    source('''
        from dataclasses import FrozenInstanceError
        from codes import Code
        good = Code("034")
        rejected = []
        for value in ["", "34", "1234", "abc", 123]:
            try:
                Code(value)
                rejected.append(False)
            except ValueError:
                rejected.append(True)
        try:
            good.value = "abc"
            frozen = False
        except FrozenInstanceError:
            frozen = True
        return [good.numeric(), rejected, frozen]
    '''),
    [34, [True, True, True, True, True], True],
))

notes = source('''
    def preview(body):
        return body

    def open_note(body):
        return body

    def export_note(body):
        return body.encode("utf-8")
''')
CASES.append(Case(
    "bounded-preview-observation",
    "Notes accept Unicode text. Opening a note and exporting it must retain the exact body. "
    "The optional compact list preview is an approximate truncation with an ellipsis; clicking "
    "it opens the full text. Preview contents never become stored text, an identifier, or exported "
    "data. The candidate adds the compact preview. These functions are the complete data path.",
    {"notes.py": notes},
    {"notes.py": notes.replace("def preview(body):\n    return body", 'def preview(body):\n    return body[:12] + "\u2026" if len(body) > 12 else body')},
    {"pragmatic": "APPROVE with risk", "pedantic": "APPROVE with risk"},
    "Slicing can sever a combining sequence at the preview boundary; the known display "
    "degradation is bounded to the truncated preview and does not corrupt retained text. Its "
    "certainty does not require inventing an unresolved premise, a storage defect, or a risk-acceptance "
    "gate. No separate Elenctic test/construction standard makes this UI strengthening mandatory.",
    source('''
        from notes import preview, open_note, export_note
        text = "01234567890e\u0301XYZ"
        return [preview(text), open_note(text) == text, export_note(text).decode("utf-8") == text]
    '''),
    ["01234567890e\u2026", True, True],
))

snapshots = source('''
    from pathlib import Path

    def save(path, text):
        Path(path).write_text(text, encoding="utf-8")
''')
CASES.append(Case(
    "optional-durability-question",
    "save writes a recreatable local snapshot. Concurrent readers must see either the previous "
    "or new complete text, not a partial write. There is one writer; paths are within one local "
    "filesystem supporting atomic replacement. At application startup the authoritative service "
    "is always reloaded and recreates this snapshot. The candidate changes replacement behavior. "
    "A proposed future offline mode has no accepted design or durability requirement.",
    {"snapshots.py": snapshots},
    {"snapshots.py": source('''
        from pathlib import Path
        from tempfile import NamedTemporaryFile
        import os

        def save(path, text):
            target = Path(path)
            temporary = None
            try:
                with NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent, delete=False) as stream:
                    temporary = stream.name
                    stream.write(text)
                os.replace(temporary, target)
            finally:
                if temporary is not None:
                    Path(temporary).unlink(missing_ok=True)
    '''),
     "DISCUSSION.md": "A reviewer asked whether future offline snapshots would survive a device losing power. "
                      "No device-specific power-loss observation or offline-mode decision is available.\n"},
    {"pragmatic": "APPROVE", "pedantic": "APPROVE"},
    "Same-filesystem replacement establishes the accepted atomic visibility obligation. Power-loss "
    "durability of a proposed offline mode remains an optional, unknown future question; it must "
    "not force INCOMPLETE or an invented premerge validation step. The executable probe checks "
    "retained text only; source and the stated filesystem contract establish the atomicity claim.",
    source('''
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from snapshots import save
        with TemporaryDirectory() as directory:
            target = Path(directory) / "snapshot"
            target.write_text("old", encoding="utf-8")
            save(target, "new complete text")
            return [target.read_text(), len(list(Path(directory).iterdir()))]
    '''),
    ["new complete text", 1],
))


def export(subjects: Path, key_path: Path, seed: int | None) -> dict:
    subjects, key_path = subjects.resolve(), key_path.resolve()
    separate(key_path, subjects)
    if subjects.exists() or key_path.exists():
        raise ValueError("export and key destinations must be new")
    rng = random.Random(seed) if seed is not None else secrets.SystemRandom()
    cases = list(CASES)
    rng.shuffle(cases)
    subjects.mkdir(parents=True, mode=0o700)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key = {"schema": "elenctic-merge-policy-key/v1", "subjects": {}}
    for case in cases:
        identity = f"{rng.getrandbits(96):024x}"
        while identity in key["subjects"]:
            identity = f"{rng.getrandbits(96):024x}"
        root = subjects / identity
        for side, files in (("base", case.base), ("candidate", case.candidate)):
            (root / side).mkdir(parents=True)
            for name, contents in files.items():
                (root / side / name).write_text(contents, encoding="utf-8")
        (root / "SUBJECT.md").write_text(
            "# Review subject\n\nCompare base/ with candidate/. These are the complete relevant source "
            "artifacts. Review the change under the supplied requirements and the separately assigned "
            "merge policy. Inspect included evidence and discussion where relevant. Return supported "
            "findings, their merge consequences, and any material limitations. Do not edit the subject. "
            "This is an offline semantic review, not a native PR campaign.\n\n## Requirements\n\n"
            + case.requirements + "\n", encoding="utf-8")
        key["subjects"][identity] = {"case": case.name, "expected": case.expected,
                                     "basis": case.basis, "digest": digest(root)}
    write_json(subjects / "manifest.json", {"schema": "elenctic-subjects/v1",
               "subjects": {identity: entry["digest"] for identity, entry in key["subjects"].items()}})
    write_json(key_path, key)
    return key


def check(subjects: Path, key_path: Path) -> list[dict]:
    subjects, key_path = subjects.resolve(), key_path.resolve()
    separate(key_path, subjects)
    key = json.loads(key_path.read_text(encoding="utf-8"))
    by_name = {case.name: case for case in CASES}
    results = []
    for identity, entry in key["subjects"].items():
        if len(identity) != 24 or any(char not in "0123456789abcdef" for char in identity):
            raise ValueError("invalid subject identity")
        root = subjects / identity
        if not root.is_dir() or digest(root) != entry["digest"]:
            raise ValueError("subject is missing or source bytes changed")
        case = by_name[entry["case"]]
        for path in root.rglob("*.py"):
            compile(path.read_text(), str(path), "exec")
        program = "import os, sys, json\nsys.path.insert(0, os.getcwd())\ndef probe():\n"
        program += textwrap.indent(case.probe, "    ") + "\nprint(json.dumps(probe()))\n"
        completed = subprocess.run([sys.executable, "-I", "-B", "-c", program],
                                   cwd=root / "candidate", capture_output=True, text=True, timeout=5)
        if completed.returncode:
            raise ValueError(f"fixture probe failed for {identity}: {completed.stderr}")
        observed = json.loads(completed.stdout)
        if observed != case.observation:
            raise ValueError(f"fixture contradicts its declared observation: {identity}")
        results.append({"subject": identity, "observed": observed})
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("export", "check"))
    parser.add_argument("--subjects", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    try:
        result = ({"subjects": len(export(args.subjects, args.key, args.seed)["subjects"])}
                  if args.command == "export" else {"probes": check(args.subjects, args.key)})
        print(json.dumps({**result, "model_evaluation": "unrun"}, indent=2))
    except (OSError, ValueError, KeyError, SyntaxError, subprocess.SubprocessError) as error:
        parser.exit(2, f"{error}\n")


if __name__ == "__main__":
    main()

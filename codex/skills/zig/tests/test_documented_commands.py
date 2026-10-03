"""Check documented runner arguments, not prose quality or Zig semantics."""
from pathlib import Path
import re
import shlex
import subprocess
import sys

from test_contracts import FAKE_ZIG
from test_tools import Fixture

ROOT = Path(__file__).resolve().parents[1]


class DocumentationCommandTests(Fixture):
    def test_documented_example_runner_commands_accept_their_arguments(self):
        self.stub("zig", FAKE_ZIG)
        commands = 0
        for source in sorted(ROOT.rglob("*.md")):
            blocks = re.findall(
                r"```(?:bash|sh|shell)\n(.*?)```",
                source.read_text(encoding="utf-8"), re.DOTALL,
            )
            for block in blocks:
                for line in block.replace("\\\n", " ").splitlines():
                    if "check_zig_examples.py" not in line:
                        continue
                    words = shlex.split(line, comments=True)
                    positions = [i for i, word in enumerate(words)
                                 if word.rsplit("/", 1)[-1] == "check_zig_examples.py"]
                    if not positions:
                        continue
                    self.assertEqual(len(positions), 1, str(source))
                    arguments = words[positions[0] + 1:]
                    commands += 1
                    with self.subTest(source=str(source.relative_to(ROOT)), arguments=arguments):
                        result = subprocess.run(
                            [sys.executable, str(ROOT / "tests" / "check_zig_examples.py"), *arguments],
                            env=self.env, capture_output=True, text=True, timeout=120,
                        )
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertGreater(commands, 0, "no documented example-runner commands found")

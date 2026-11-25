"""Offline cc readback checks, including real Git results; no model is called.

usage: uv run --no-project python -I agents/skills/cc/tests/test_cc.py
"""

import copy
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "readback.py"
SID = "11111111-2222-4333-8444-555555555555"
MODEL = "claude-opus-5-5"
BASE = "04c0a84a962c3e637c14614498aa1950a776ba6e"
PROMPT = b"Perform one independent, read-only code review.\n\n{\"lens_name\": \"fresh-eyes\"}"
PATCH = "diff --git a/check.txt b/check.txt\n@@ -1 +1 @@\n-before\n+after\n"
checks = 0


FORK = "forked-command-code-review"


def init_event(tools=("Task", "Bash", "Glob", "Grep", "Read")):
    # Shaped like live 2.1.33x init events, which carry these runtime facts.
    return {"type": "system", "subtype": "init", "session_id": SID, "model": MODEL,
            "claude_code_version": "2.1.331", "tools": list(tools), "permissionMode": "dontAsk",
            "mcp_servers": [], "plugins": [{"name": "managed-plugin", "path": "/managed/plugin"}]}


def standard_events(level="high", target=BASE, command=None, output=PATCH, result="(none)"):
    # A prompt-started /review streams its forked messages under a forked-command- parent,
    # and its tool results carry no tool_use_result metadata (observed live).
    return [
        init_event(),
        {"type": "user", "parent_tool_use_id": FORK, "message": {"content": [{"type": "text", "text":
            f"Review target: `{target}`\n\n`{level} effort → 8 inline angles → ≤10 findings`\n\n## Phase 1"}]}},
        {"type": "assistant", "parent_tool_use_id": FORK, "message": {"content": [{"type": "tool_use",
            "id": "diff-1", "name": "Bash", "input": {"command": command or f"git diff {target[:12]} HEAD"}}]}},
        {"type": "user", "parent_tool_use_id": FORK, "message": {"content": [{"type": "tool_result",
            "tool_use_id": "diff-1", "is_error": False, "content": output}]}},
        {"type": "result", "subtype": "success", "is_error": False, "session_id": SID,
         "modelUsage": {MODEL: {}}, "permission_denials": [], "result": result},
    ]


def as_followup(events, tool_id="diff-2"):
    """Reshape a /review fixture as a resumed main-conversation stream, as observed live."""
    stream = copy.deepcopy(events)
    del stream[1]
    request, response = stream[1], stream[2]
    request["parent_tool_use_id"] = response["parent_tool_use_id"] = None
    request["message"]["content"][0]["id"] = response["message"]["content"][0]["tool_use_id"] = tool_id
    response["tool_use_result"] = {"stdout": "", "stderr": "", "interrupted": False}
    return stream


def custom_events():
    output = {"findings": [], "overall_correctness": "patch is correct",
              "overall_explanation": "Inspected the whole changeset.", "overall_confidence_score": 0.8}
    return [
        init_event(("Bash", "Glob", "Grep", "Read", "StructuredOutput")),
        {"type": "result", "subtype": "success", "is_error": False, "session_id": SID,
         "modelUsage": {MODEL: {}}, "permission_denials": [], "result": "", "structured_output": output},
    ]


def answered(stream, reply):
    """A follow-up stream whose main thread answers with message REPLY, as its transcript records it."""
    stream = copy.deepcopy(stream)
    stream.insert(-1, {"type": "assistant", "parent_tool_use_id": None, "message": {"id": reply, "content": []}})
    return stream


def reply(message_id):
    return {"type": "assistant", "sessionId": SID, "message": {"id": message_id, "content": []}}


def transcript(prompt=PROMPT):
    return [
        {"type": "queue-operation", "sessionId": SID},
        {"type": "user", "isMeta": True, "sessionId": SID, "message": {"content": "<meta>"}},
        {"type": "user", "sessionId": SID, "message": {"content": prompt.decode()}},
        {"type": "assistant", "sessionId": SID, "message": {"content": []}},
    ]


def json_lines(records):
    return records if isinstance(records, str) else "".join(json.dumps(r) + "\n" for r in records)


def readback(base: Path, kind: str, events, records=None, prompt=PROMPT, extra_transcript=False, target=BASE,
             followups=(), reference_patch=None, env_extra=None, cwd=None, followup_prompts=()):
    tmp = Path(tempfile.mkdtemp(dir=base))
    events_path, out = tmp / "events.jsonl", tmp / "out.json"
    events_path.write_text(json_lines(events), encoding="utf-8")
    config = tmp / "config"
    if records is not None:
        project = config / "projects" / "-repo"
        project.mkdir(parents=True)
        (project / f"{SID}.jsonl").write_text(json_lines(records), encoding="utf-8")
        if extra_transcript:
            other = config / "projects" / "-elsewhere"
            other.mkdir(parents=True)
            (other / f"{SID}.jsonl").write_text("", encoding="utf-8")
    prompt_path = tmp / "prompt.txt"
    prompt_path.write_bytes(prompt)
    args = ([kind, str(events_path), SID, MODEL, target, "high", str(out)] if kind == "standard"
            else [kind, str(events_path), SID, MODEL, str(prompt_path), str(out)])
    if reference_patch is not None:
        args.extend(["--reference-patch", str(reference_patch)])
    for index, stream in enumerate(followups):
        path = tmp / f"followup-{index}.jsonl"
        path.write_text(json_lines(stream), encoding="utf-8")
        args.extend(["--followup", str(path)])
    for index, followup_prompt in enumerate(followup_prompts):
        path = followup_prompt if isinstance(followup_prompt, Path) else tmp / f"followup-prompt-{index}.txt"
        if not isinstance(followup_prompt, Path):
            path.write_bytes(followup_prompt)
        args.extend(["--followup-prompt", str(path)])
    # sys.executable is the interpreter selected by the outer UV invocation.
    proc = subprocess.run([sys.executable, "-I", str(SCRIPT), *args],
                          env={**os.environ, "CLAUDE_CONFIG_DIR": str(config), **(env_extra or {})},
                          cwd=cwd, capture_output=True, text=True)
    assert out.exists(), proc.stderr
    report = json.loads(out.read_text(encoding="utf-8"))
    assert (proc.returncode == 0) == report["ok"], proc.stderr
    assert "Traceback" not in proc.stderr, proc.stderr
    return report


def expect(report, fragment=None):
    global checks
    if fragment is None:
        assert report["ok"], report["problems"]
    else:
        assert not report["ok"] and any(fragment in p for p in report["problems"]), (fragment, report)
    checks += 1


def git_observations(tmp):
    repo = tmp / "git-subject"
    repo.mkdir()
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}

    def git(*args, cwd=repo):
        return subprocess.run(["git", "-c", "core.hooksPath=" + os.devnull,
                               "-c", "commit.gpgsign=false", "-c", "user.name=CC fixture",
                               "-c", "user.email=cc-fixture@example.invalid", *args],
                              cwd=cwd, env=env, capture_output=True, text=True)

    def success(*args):
        run = git(*args)
        assert run.returncode == 0, run.stderr
        return run.stdout.strip()

    success("init", "-q")
    source = repo / "check.txt"
    source.write_text("before\n", encoding="utf-8")
    success("add", "check.txt")
    success("commit", "-qm", "base")
    target = success("rev-parse", "HEAD")
    source.write_text("after\n", encoding="utf-8")
    success("add", "check.txt")
    success("commit", "-qm", "head")
    patch = git("diff", target, "HEAD")
    assert patch.returncode == 0 and "diff --git" in patch.stdout
    outside = tmp / "not-a-repository"
    outside.mkdir()
    failed = git("diff", target, cwd=outside)
    assert failed.returncode == 129, (failed.returncode, failed.stderr)
    changed = git("diff", "--exit-code", target, "HEAD")
    assert changed.returncode == 1 and changed.stdout == patch.stdout
    scoped = git("diff", "--unified=20", target, "HEAD", "--", "check.txt")
    assert scoped.returncode == 0 and "diff --git" in scoped.stdout
    return target, patch, failed, changed, scoped


def launch_effort(tmp):
    global checks
    skill = SCRIPT.parent.parent
    blocks = re.findall(r"^[ \t]*```bash\n(.*?)\n[ \t]*```", (skill / "SKILL.md").read_text(), re.S | re.M)
    for block in blocks:
        subprocess.run(["bash", "-n"], input=block, text=True, check=True)
    launch = next(block for block in blocks if "\n# Standard\n" in block)
    setup, commands = launch.split("\n# Standard\n", 1)
    standard, custom = commands.split("\n# Custom: $prompt holds the exact instruction bytes\n", 1)
    binary = tmp / "launch-bin"
    binary.mkdir()
    stub = binary / "claude"
    stub.write_text('''#!/bin/bash
printf 'environment=%s\\nlocks=%s\\nbackground=%s\\n' "$CLAUDE_CODE_EFFORT_LEVEL" "$GIT_OPTIONAL_LOCKS" \\
  "${CLAUDE_CODE_DISABLE_BACKGROUND_TASKS-unset}"
while (($#)); do
  if [[ "$1" == "--effort" ]]; then printf 'flag=%s\\n' "$2"; fi
  if [[ "$1" == "--session-id" ]]; then printf 'session=%s\\n' "$2"; fi
  if [[ "$1" == "--resume" ]]; then printf 'resume=%s\\n' "$2"; fi
  shift
done
cat >"$stdin_capture"
''')
    stub.chmod(0o755)
    repo = tmp / "launch subject with spaces"
    repo.mkdir()
    prompt = tmp / "launch prompt with spaces"
    prompt.write_bytes(PROMPT)
    followup = tmp / "launch followup prompt with spaces"
    followup_bytes = b"Complete the missing target read and reassess the original findings.\n\n"
    followup.write_bytes(followup_bytes)
    fresh_sid = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
    settings = tmp / "launch-settings.json"
    settings.write_text("{}\n")
    resume = textwrap.dedent(next(block for block in blocks if "--resume" in block)).split("\n", 1)[1]
    assert resume.strip() == standard.strip().replace('--session-id "$sid"', '--resume "$sid"').replace(
        '"/review $level $base..HEAD" </dev/null >"$events" 2>"$diagnostics")',
        '<"$followup_prompt" >"$followup_events" 2>"$followup_diagnostics")'), resume
    for kind, command, prompt_bytes in [("standard", standard, b""), ("custom", custom, PROMPT),
                                       ("resume", resume, followup_bytes)]:
        for selected, inherited in [("high", "low"), ("low", "max")]:
            events = tmp / f"launch-{kind}-{selected}.jsonl"
            stdin_capture = tmp / f"launch {kind} {selected} stdin"
            env = {**os.environ, "PATH": str(binary) + os.pathsep + os.environ["PATH"],
                   "CLAUDE_CODE_EFFORT_LEVEL": inherited, "selected_effort": selected,
                   "repo": str(repo), "selected_model": MODEL, "level": "high", "base": BASE,
                   "settings": str(settings), "events": str(events),
                   "diagnostics": str(tmp / "launch-errors"), "prompt": str(prompt), "skill_dir": str(skill),
                   "stdin_capture": str(stdin_capture), "followup_prompt": str(followup), "followup_events": str(events),
                   "followup_diagnostics": str(tmp / "launch-errors")}
            session = f"sid={shlex.quote(SID)}\n" if kind == "resume" else ""
            script = f"uuidgen() {{ printf '%s\\n' '{fresh_sid}'; }}\n" + setup + "\n" + session + command
            # A closed stdin makes a lost redirect fail instead of blocking on a terminal.
            run = subprocess.run(["bash", "-eu", "-c", script], env=env, capture_output=True, text=True,
                                 stdin=subprocess.DEVNULL)
            assert run.returncode == 0, run.stderr
            observed = dict(line.split("=", 1) for line in events.read_text().splitlines())
            expected = {"environment": selected, "locks": "0", "background": "1", "flag": selected}
            assert observed == {**expected, **({"resume": SID} if kind == "resume" else {"session": fresh_sid})}, observed
            delivered = stdin_capture.read_bytes()
            assert delivered == prompt_bytes, (kind, delivered)
            checks += 1


def chain_checks(tmp):
    repo = tmp / "chain-subject"
    repo.mkdir()
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_OPTIONAL_LOCKS": "0"}

    def git(*args):
        run = subprocess.run(["git", "-c", "core.hooksPath=" + os.devnull,
                              "-c", "commit.gpgsign=false", "-c", "user.name=CC fixture",
                              "-c", "user.email=cc-fixture@example.invalid", *args],
                             cwd=repo, env=env, capture_output=True, text=True)
        assert run.returncode == 0, run.stderr
        return run.stdout.strip()

    git("init", "-q")
    (repo / ".gitattributes").write_text("z.txt diff=fail\n")
    for name in ("a.txt", "z.txt"):
        (repo / name).write_text("before\n")
    git("add", ".")
    git("commit", "-qm", "base")
    target = git("rev-parse", "HEAD") + "..HEAD"
    for name in ("a.txt", "z.txt"):
        (repo / name).write_text("after\n")
    git("add", ".")
    git("commit", "-qm", "head")

    def observation(command):
        run = subprocess.run(["bash", "-c", command], cwd=repo, env=env, capture_output=True, text=True)
        events = standard_events(target=target, command=command, output=run.stdout + run.stderr)
        events[3]["message"]["content"][0].update(is_error=run.returncode != 0, exit_code=run.returncode)
        assert git("status", "--porcelain") == ""
        return events, run

    for command in [f"git diff {target} && git diff HEAD",
                    f"git diff {target} --stat; git diff {target}",
                    f"git diff {target} --stat && git diff {target} && git status --short && ls -la"]:
        events, run = observation(command)
        assert run.returncode == 0
        expect(readback(tmp, "standard", events, target=target))
    # Quoted operators are literal paths, so this is one direct read; naming paths that do not
    # exist observes nothing, and an empty path-limited read must show a patch to count.
    events, run = observation(f"git diff {target} -- 'literal;path' 'literal&&path'")
    report = readback(tmp, "standard", events, target=target)
    expect(report, "every recognized read failed")
    assert report["diff_reads"][0]["shape"] == "direct", report
    assert report["diff_reads"][0]["reason"] == "current-diff or path-limited read showed no patch", report

    original, run = observation(f"git diff {target}; git diff HEAD")
    assert run.returncode == 0 and "diff --git" in run.stdout
    report = readback(tmp, "standard", original, target=target)
    expect(report, "completion is unverified")
    assert "completion status is unavailable" in report["diff_reads"][0]["reason"]
    assert all(route in " ".join(report["problems"]) for route in ("--reference-patch", "--followup")), report
    reference = tmp / "complete-reference.patch"
    reference.write_bytes(run.stdout.encode())
    report = readback(tmp, "standard", original, target=target, reference_patch=reference)
    expect(report)
    assert report["diff_reads"][0].get("reference_matched"), report
    assert report["diff_reads"][0]["completion_status"] == "unknown", report
    assert report["result"] == original[-1]["result"]
    assert report["reference_patch"] == {"path": str(reference),
        "sha256": hashlib.sha256(reference.read_bytes()).hexdigest(), "patch_text": True}, report
    for output in [run.stdout.removesuffix("\n"), "before read\n" + run.stdout + "after read\n"]:
        transported = copy.deepcopy(original)
        transported[3]["message"]["content"][0]["content"] = output
        report = readback(tmp, "standard", transported, target=target, reference_patch=reference)
        expect(report)
        assert report["diff_reads"][0]["completion_status"] == "unknown"
    truncated = copy.deepcopy(original)
    content = truncated[3]["message"]["content"][0]["content"]
    truncated[3]["message"]["content"][0]["content"] = content[:content.rindex("diff --git")]
    expect(readback(tmp, "standard", truncated, target=target, reference_patch=reference),
           "completion is unverified")
    for output in [content.removesuffix("\n") + "_WRONG\n", "prefix" + content,
                   content.replace("-before\n", "", 1)]:
        mismatched = copy.deepcopy(original)
        mismatched[3]["message"]["content"][0]["content"] = output
        report = readback(tmp, "standard", mismatched, target=target, reference_patch=reference)
        expect(report, "completion is unverified")
        assert not report["diff_reads"][0].get("reference_matched"), report
        assert "supply an authenticated --reference-patch" not in " ".join(report["problems"]), report
        assert "resume the same session" in " ".join(report["problems"]), report
    blank_terminated = tmp / "blank-terminated-reference.patch"
    blank_terminated.write_bytes(reference.read_bytes() + b"\n")
    expect(readback(tmp, "standard", original, target=target, reference_patch=blank_terminated))
    missing_blank = copy.deepcopy(original)
    missing_blank[3]["message"]["content"][0]["content"] = content.removesuffix("\n")
    expect(readback(tmp, "standard", missing_blank, target=target, reference_patch=blank_terminated),
           "completion is unverified")
    for invalid_target in ["--output=x..HEAD", "-", "not-a-commit..HEAD"]:
        expect(readback(tmp, "standard", original, target=invalid_target, reference_patch=reference),
               "cannot compare reference patch for target")
    assert not any(repo.glob("x*"))
    for data, error in [(b"", "reference patch contains no patch text"),
                        (b"a.txt | 2 +-\n", "reference patch contains no patch text"),
                        (b"diff --git a/a.txt b/a.txt\n+\xff\n", "cannot read reference patch")]:
        invalid_reference = tmp / "invalid-reference.patch"
        invalid_reference.write_bytes(data)
        expect(readback(tmp, "standard", original, target=target, reference_patch=invalid_reference), error)
    for missing_reference in [tmp / "missing-reference.patch", repo]:
        expect(readback(tmp, "standard", original, target=target, reference_patch=missing_reference),
               "cannot read reference patch")
    for flags in [["--reference-patch", "a", "--reference-patch", "b"], ["--replay-repo", str(repo)]]:
        rejected_flag = subprocess.run([sys.executable, "-I", str(SCRIPT), "standard", "events", SID, MODEL,
                                        target, "high", "out", *flags], capture_output=True, text=True)
        assert rejected_flag.returncode != 0 and "usage:" in rejected_flag.stderr
    supplemental = as_followup(observation(f"git diff {target}")[0])
    supplemental[-1]["result"] = "Completed the missing read and reassessed it: a.txt:1 has a defect."
    denied = [{"tool_name": "Bash", "tool_input": {"command": "npm test"}}]
    supplemental[-1]["permission_denials"] = denied
    report = readback(tmp, "standard", original, target=target, followups=[supplemental])
    expect(report)
    assert report["result"] == original[-1]["result"]
    assert [read["ok"] for read in report["diff_reads"]] == [False, True]
    assert report["diff_reads"][1]["followup"] == 1
    assert report["followups"][0]["result"] == supplemental[-1]["result"]
    assert report["followups"][0]["permission_denials"] == denied and report["permission_denials"] == []
    for index, key, value, error in [(0, "session_id", "other", "init session"),
                                    (0, "model", "other", "init model"),
                                    (-1, "subtype", "error_during_execution", "result is"),
                                    (-1, "result", "", "nonempty follow-up")]:
        invalid = copy.deepcopy(supplemental)
        invalid[index][key] = value
        expect(readback(tmp, "standard", original, target=target, followups=[invalid]), error)
    expect(readback(tmp, "standard", original, target=target, followups=[supplemental[:-1]]), "not terminal")
    duplicate = copy.deepcopy(supplemental)
    duplicate[1]["message"]["content"][0]["id"] = "diff-1"
    duplicate[2]["message"]["content"][0]["tool_use_id"] = "diff-1"
    expect(readback(tmp, "standard", original, target=target, followups=[duplicate]), "no successful correlated")
    wrong_target = copy.deepcopy(supplemental)
    wrong_target[1]["message"]["content"][0]["input"]["command"] = "git diff " + "f" * 40 + "..HEAD"
    expect(readback(tmp, "standard", original, target=target, followups=[wrong_target]), "no successful correlated")
    failed = copy.deepcopy(supplemental)
    failed[2]["message"]["content"][0].update(is_error=True, exit_code=128, content="fatal: failed read")
    expect(readback(tmp, "standard", original, target=target, followups=[failed]), "no successful correlated")
    second = copy.deepcopy(supplemental)
    second[1]["message"]["content"][0]["id"] = "diff-3"
    second[2]["message"]["content"][0]["tool_use_id"] = "diff-3"
    report = readback(tmp, "standard", original, target=target, followups=[failed, second])
    expect(report)
    assert [read["ok"] for read in report["diff_reads"]] == [False, False, True]

    for separator in ["';'", "'&&'", r"\;", r"\&\&"]:
        events, run = observation(f"git rev-parse -- 'diff --git a/x b/x' {separator} git diff {target}")
        assert run.returncode == 0 and "diff --git" in run.stdout
        expect(readback(tmp, "standard", events, target=target), "no successful correlated")
    events, run = observation(f"git diff {target} -- ':(bogus)x'; git ls-files --format='diff --git %(path)'")
    assert run.returncode == 0 and "diff --git" in run.stdout and "fatal:" in run.stderr
    expect(readback(tmp, "standard", events, target=target), "no successful correlated")
    failed_target = subprocess.run(["git", "diff", target, "--", ":(bogus)x"],
                                   cwd=repo, env=env, capture_output=True, text=True)
    assert failed_target.returncode == 128 and not failed_target.stdout
    for output, matched in [(content, True), (content.removesuffix("\n") + "_WRONG\n", False)]:
        formatted = output.replace("%", "%x25").replace("\n", "%x0a")
        events, run = observation(f"git diff {target} -- ':(bogus)x'; "
                                 f"git ls-files --format={shlex.quote(formatted)} -- a.txt")
        assert run.returncode == 0 and "fatal:" in run.stderr
        assert (content in run.stdout) == matched
        report = readback(tmp, "standard", events, target=target, reference_patch=reference)
        expect(report, None if matched else "completion is unverified")
        assert report["diff_reads"][0].get("reference_matched", False) == matched, report
        assert report["diff_reads"][0]["completion_status"] == "unknown", report
    # A companion's exit 1 must not borrow a later, unexecuted diff's --exit-code meaning.
    events, run = observation(f"git ls-files --format='diff --git %(path)' && "
                              f"git check-ignore a.txt && git diff --exit-code {target}")
    assert run.returncode == 1 and "diff --git" in run.stdout
    expect(readback(tmp, "standard", events, target=target), "no successful correlated")

    git("config", "diff.fail.textconv", "false")
    direct, run = observation(f"git diff {target}")
    assert run.returncode == 128 and "diff --git a/a.txt" in run.stdout and "fatal:" in run.stderr
    expect(readback(tmp, "standard", direct, target=target), "no successful correlated")
    events, run = observation(f"git diff {target}; git diff HEAD")
    assert run.returncode == 0 and "diff --git a/a.txt" in run.stdout and "fatal:" in run.stderr
    expect(readback(tmp, "standard", events, target=target), "no successful correlated")
    report = readback(tmp, "standard", events, target=target, reference_patch=reference)
    expect(report, "completion is unverified")
    assert not report["diff_reads"][0].get("reference_matched"), report


def reference_boundary(tmp):
    repo = tmp / "reference-boundary-subject"
    repo.mkdir()
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_OPTIONAL_LOCKS": "0"}

    def git(*args):
        run = subprocess.run(["git", "-c", "core.hooksPath=" + os.devnull,
                              "-c", "commit.gpgsign=false", "-c", "user.name=CC fixture",
                              "-c", "user.email=cc-fixture@example.invalid", *args],
                             cwd=repo, env=env, capture_output=True, text=True)
        assert run.returncode == 0, run.stderr
        return run.stdout

    git("init", "-q")
    (repo / ".gitattributes").write_text("sample.txt diff=probe\n")
    source, protected = repo / "sample.txt", repo / "protected.txt"
    source.write_text("before\n")
    protected.write_text("original tracked contents\n")
    git("add", ".")
    git("commit", "-qm", "base")
    target = git("rev-parse", "HEAD").strip() + "..HEAD"
    source.write_text("after\n")
    git("add", ".")
    git("commit", "-qm", "head")
    head = git("rev-parse", "HEAD")
    reference = tmp / "boundary-reference.patch"
    reference.write_bytes(git("diff", target, "--").encode())
    command = f"git diff {target}; git diff HEAD"
    observed = subprocess.run(["bash", "-c", command], cwd=repo, env=env, capture_output=True, text=True)
    assert observed.returncode == 0 and observed.stdout == reference.read_text()
    events = standard_events(target=target, command=command, output=observed.stdout)
    events[3]["message"]["content"][0]["exit_code"] = observed.returncode

    converter = tmp / "writing-textconv"
    converter.write_text("#!/bin/sh\nprintf 'changed by textconv\\n' >" + shlex.quote(str(protected)) +
                         '\ncat "$1"\n')
    converter.chmod(0o755)
    git("config", "diff.probe.textconv", shlex.quote(str(converter)))
    git("config", "diff.probe.cachetextconv", "true")
    assert git("diff", target, "--") == reference.read_text()
    assert protected.read_text() == "changed by textconv\n"
    assert "refs/notes/textconv/probe" in git("for-each-ref", "--format=%(refname)")
    protected.write_text("original tracked contents\n")
    git("update-ref", "-d", "refs/notes/textconv/probe")
    assert git("status", "--porcelain") == ""

    binary = tmp / "reference-bin"
    binary.mkdir()
    invoked = tmp / "unexpected-git-invocation"
    stub = binary / "git"
    stub.write_text("#!/bin/sh\nprintf 'invoked\\n' >" + shlex.quote(str(invoked)) + "\nexit 97\n")
    stub.chmod(0o755)
    report = readback(tmp, "standard", events, target=target, reference_patch=reference, cwd=repo,
                      env_extra={**env, "PATH": str(binary) + os.pathsep + env["PATH"]})
    expect(report)
    assert report["diff_reads"][0].get("reference_matched")
    assert not invoked.exists()
    assert protected.read_text() == "original tracked contents\n"
    assert "refs/notes/textconv/probe" not in git("for-each-ref", "--format=%(refname)")
    assert git("rev-parse", "HEAD") == head and git("status", "--porcelain") == ""


def inquiry_diagnostics(tmp):
    supplemental = as_followup(standard_events(command=f"git diff {BASE}..HEAD", result="Eight agents are running."))
    expect(readback(tmp, "standard", standard_events(), followups=[supplemental]))

    requests = [f"git diff {BASE}..HEAD --stat", f"git log --oneline {BASE}..HEAD | head -50",
                "git show --stat HEAD~1 HEAD~2", "git show HEAD~1 -- native/main.zig",
                f"B={BASE}; for f in a b; do git diff $B..HEAD -- $f; done",
                f"git -c core.fsmonitor=false diff {BASE}..HEAD", f"git -C /repo diff {BASE}..HEAD",
                f"echo 'git diff {BASE}..HEAD'", "ls -la"]
    for command in requests:
        report = readback(tmp, "standard", standard_events(command=command))
        expect(report, "other Bash requests did not establish a target patch read")
        assert any("resume the same session with the bound launch settings" in p and "--followup" in p
                   for p in report["problems"]), report
        assert report["other_bash_requests"] == [{"tool_use_id": "diff-1", "command": command}], report
        assert "other_git_reads" not in report, report
    non_bash = standard_events()
    non_bash[2]["message"]["content"][0].update(name="Read", input={"file_path": "/repo/check.txt"})
    report = readback(tmp, "standard", non_bash)
    expect(report, "no recognized target diff request was found")
    assert report["other_bash_requests"] == [], report
    failed = standard_events(output="Exit code 128\nfatal: bad revision")
    failed[3]["message"]["content"][0]["is_error"] = True
    report = readback(tmp, "standard", failed)
    expect(report, "every recognized read failed, lacks a unique later result, or did not reach the reviewer")
    assert any("dependent reassessment" in p and "--followup" in p for p in report["problems"]), report
    original = standard_events(command=requests[0])
    report = readback(tmp, "standard", original, followups=[supplemental])
    expect(report)
    assert "other_bash_requests" not in report and report["result"] == original[-1]["result"], report
    assert [read.get("followup") for read in report["diff_reads"]] == [1], report
    supplemental[1]["message"]["content"][0]["input"]["command"] = "ls -la"
    report = readback(tmp, "standard", original, followups=[supplemental])
    expect(report, "other Bash requests did not establish a target patch read")
    assert report["other_bash_requests"] == [
        {"tool_use_id": "diff-1", "command": requests[0]},
        {"tool_use_id": "diff-2", "command": "ls -la", "followup": 1}], report


def terminal_evidence(tmp):
    origins = [{"kind": "task-notification", "producer": "session-task"},
               *({"kind": "task-notification", "subkind": subkind} for subkind in
                 ("scheduled-trigger", "peer-send-message", "external-event"))]
    for origin in origins:
        events = standard_events()
        events[-1]["origin"] = origin
        report = readback(tmp, "standard", events)
        expect(report, "unexpected non-human result origin:")
        assert report["origin"] == origin and report["result"] == events[-1]["result"], report
        assert "results" not in report, report
        diagnosis = next(p for p in report["problems"] if "unexpected non-human result origin:" in p)
        assert all(value in diagnosis for value in origin.values()), report
        assert not any("expected one" in p or "background-task wakes" in p
                       or "CLAUDE_CODE_DISABLE_BACKGROUND_TASKS" in p for p in report["problems"]), report

    for origin in [{"kind": "auto-continuation"}, {"subkind": "scheduled-trigger"}, "human"]:
        events = standard_events()
        events[-1]["origin"] = origin
        expect(readback(tmp, "standard", events), "unexpected non-human result origin:")
        followup = as_followup(standard_events())
        followup[-1]["origin"] = origin
        expect(readback(tmp, "standard", standard_events(), followups=[followup]),
               "follow-up 1: unexpected non-human result origin:")
    events = standard_events()
    events[-1]["origin"] = {"kind": "human"}
    report = readback(tmp, "standard", events)
    expect(report)
    assert report["origin"] == events[-1]["origin"] and "results" not in report, report

    original = standard_events(result="check.txt:1 — invalid inputs are accepted.")
    original[-1]["permission_denials"] = [{"tool_name": "Bash", "tool_input": {"command": "npm test"}}]
    supplemental = as_followup(original)
    wake = [{"type": "system", "subtype": "init", "session_id": SID, "model": MODEL},
            {"type": "result", "subtype": "success", "is_error": False, "session_id": SID,
             "modelUsage": {MODEL: {}}, "result": "The later task found a second issue.",
             "origin": origins[0],
             "permission_denials": [{"tool_name": "Bash", "tool_input": {"command": "git -C /repo show"}}]}]
    for stream, followups, prefix in [(original + wake, [], ""),
                                      (standard_events(), [supplemental + wake], "follow-up 1: ")]:
        report = readback(tmp, "standard", stream, followups=followups)
        expect(report, prefix + "expected one terminal result, found 2")
        assert prefix + "expected one init event, found 2" in report["problems"], report
        assert any(p.startswith(prefix + "unexpected non-human result origin:")
                   for p in report["problems"]), report
        held = report["followups"][0] if followups else report
        expected = [event for event in (followups[0] if followups else stream) if event.get("type") == "result"]
        assert held["result"] is None and held["results"] == expected, report
        assert held["permission_denials"] == expected[0]["permission_denials"] + expected[1]["permission_denials"], report

    custom_stream = custom_events()
    custom_stream[-1]["result"] = "Original custom review."
    custom_stream[-1]["structured_output"]["findings"] = [{"title": "Original finding"}]
    custom_stream += copy.deepcopy(wake)
    report = readback(tmp, "custom", custom_stream, transcript())
    expect(report, "expected one terminal result, found 2")
    assert report["result"] is None, report
    assert report["results"] == [event for event in custom_stream if event.get("type") == "result"], report

    for key, value, error in [("modelUsage", {"other-model": {}}, "models used"),
                              ("subtype", "error_during_execution", "result is error_during_execution"),
                              ("permission_denials", {}, "permission_denials is not an array")]:
        events = standard_events()
        first = copy.deepcopy(events[-1])
        first[key] = value
        events.insert(-1, first)
        report = readback(tmp, "standard", events)
        expect(report, error)
        assert report["result"] is None and report["results"] == [first, events[-1]], report
    recovered = readback(tmp, "standard", original + wake, followups=[supplemental])
    expect(recovered, "expected one terminal result, found 2")
    assert recovered["result"] is None and recovered["followups"][0]["result"] == supplemental[-1]["result"], recovered

    # A follow-up only adds reads, so the read-gap hold names it only when nothing else holds.
    hidden = f"git diff {BASE}..HEAD; git ls-files"
    for events, extra in [(standard_events(command=f"git diff {BASE}..HEAD --stat") + wake, "terminal result"),
                          (standard_events(level="low", command=hidden), "recipe ran at low effort")]:
        report = readback(tmp, "standard", events)
        expect(report, extra)
        gap = next(p for p in report["problems"] if p.startswith("no successful correlated"))
        assert "a --followup cannot clear" in gap and "resume the same session" not in gap, report
        assert "--reference-patch" not in gap, report
    report = readback(tmp, "standard", standard_events(command=hidden))
    expect(report, "completion is unverified")
    assert len(report["problems"]) == 1 and "--reference-patch" in report["problems"][0], report
    assert "resume the same session with the bound launch settings" in report["problems"][0], report


def persisted_reads(tmp):
    global checks

    preview = f"<persisted-output>\nOutput too large (1.9MB). Full output saved to: /x/tool-results/b.txt\n\nPreview (first 2KB):\n{PATCH}"
    # Forked /review results carry only the content wrapper; resumed main-conversation
    # results also carry tool_use_result metadata.
    report = readback(tmp, "standard", standard_events(output=preview))
    expect(report)
    assert report["diff_reads"][0]["persisted_output"] is True, report
    followup = as_followup(standard_events())
    followup[2]["tool_use_result"]["persistedOutputPath"] = "/x/b.txt"
    report = readback(tmp, "standard", standard_events(command="ls -la"), followups=[followup])
    expect(report)
    assert report["diff_reads"][0]["persisted_output"] is True and report["diff_reads"][0]["followup"] == 1, report
    assert "persisted_output" not in readback(tmp, "standard", standard_events())["diff_reads"][0]
    checks += 1
    reference = tmp / "persisted-reference.patch"
    reference.write_text(PATCH, encoding="utf-8")
    hidden = standard_events(command=f"git diff {BASE}..HEAD; git ls-files", output=preview)
    report = readback(tmp, "standard", hidden, reference_patch=reference)
    expect(report)
    read = report["diff_reads"][0]
    assert read["persisted_output"] and read["reference_matched"] and read["completion_status"] == "unknown", report
    failed = standard_events(output=preview)
    failed[3]["message"]["content"][0]["is_error"] = True
    report = readback(tmp, "standard", failed)
    expect(report, "every recognized read failed, lacks a unique later result, or did not reach the reviewer")
    assert report["diff_reads"][0]["persisted_output"] and not report["diff_reads"][0]["ok"], report
    failed = as_followup(standard_events(output=preview))
    failed[2]["tool_use_result"].update(exitCode=128, persistedOutputPath="/x/b.txt")
    report = readback(tmp, "standard", standard_events(command="ls -la"), followups=[failed])
    expect(report, "every recognized read failed, lacks a unique later result, or did not reach the reviewer")
    assert report["diff_reads"][0]["persisted_output"] and not report["diff_reads"][0]["ok"], report


def runtime_evidence(tmp):
    report = readback(tmp, "standard", standard_events())
    expect(report)
    assert report["runtime"] == {"claude_code_version": "2.1.331", "tools": ["Task", "Bash", "Glob", "Grep", "Read"],
                                 "permission_mode": "dontAsk", "mcp_servers": [],
                                 "plugins": [{"name": "managed-plugin", "path": "/managed/plugin"}]}, report
    assert report["recipe_parent_tool_use_id"] == FORK, report
    for key, value, error in [("claude_code_version", "2.1.286", "is not 2.1.287 or newer"),
                              ("claude_code_version", "2.1.1000", None), ("claude_code_version", "3.0.0", None),
                              ("claude_code_version", None, "is not 2.1.287 or newer"),
                              ("claude_code_version", "2.1.x", "is not 2.1.287 or newer"),
                              ("tools", ["Task", "Bash", "Read", "Write"], "exceed the standard launch inventory"),
                              ("tools", ["Agent", "Bash", "Read"], None),
                              ("tools", ["Bash", "mcp__x__y"], "exceed the standard launch inventory"),
                              ("tools", "Bash", "is not a list of tool names"),
                              ("permissionMode", "default", "is not dontAsk"),
                              ("mcp_servers", [{"name": "x"}], "is not empty"),
                              ("mcp_servers", None, "is not empty")]:
        events = standard_events()
        events[0][key] = value
        expect(readback(tmp, "standard", events), error)
    current = standard_events()
    current[1]["message"]["content"][0]["text"] = "`high effort → 8 inline angles → ≤10 findings`\n\n## Phase 1"
    report = readback(tmp, "standard", current, target="-")
    expect(report)
    assert report["observed_level"] == "high" and report["recipe_parent_tool_use_id"] == FORK, report
    held = "no successful correlated `git diff` read against the current diff"
    # The helper cannot resolve the current-diff scope, so an unchained direct read counts when its own
    # result shows a patch; whether the reads cover the bound scope is the caller's judgment.
    for command, output, error in [
            ("git diff origin/HEAD...HEAD", PATCH, None), ("git diff @{upstream}...HEAD", PATCH, None),
            ("git diff origin/release+1...HEAD", PATCH, None), ("git diff HEAD~1", PATCH, None),
            ("git diff HEAD", PATCH, None), ("git diff @", PATCH, None),
            ("git diff --stat origin/HEAD...HEAD", PATCH, held), ("git diff --output=/tmp/x HEAD", PATCH, held),
            ("ls -la", PATCH, held),
            # A chain's output cannot be attributed to one read: the patch may come from a companion.
            ("git diff @...HEAD && git diff HEAD", PATCH, held), ("git diff origin/HEAD...HEAD; git diff .", PATCH, held),
            ("git diff --stat origin/HEAD...HEAD && git diff origin/HEAD...HEAD", PATCH, held)] + [
            (command, "", held) for command in ("git diff origin/HEAD...HEAD", "git diff .", "git diff HEAD^{}...HEAD",
                                                "git diff @{0}...HEAD", "git diff HEAD")]:
        stream = standard_events(command=command, output=output)
        stream[1]["message"]["content"][0]["text"] = current[1]["message"]["content"][0]["text"]
        report = readback(tmp, "standard", stream, target="-")
        expect(report, error)
        assert error is None or "`git diff <upstream>...HEAD`" in report["problems"][-1], report
        assert "--reference-patch" not in " ".join(report["problems"]), report
    # With a bound target, only the target line identifies the recipe, not an earlier effort mention.
    mention = standard_events()
    mention.insert(1, {"type": "user", "parent_tool_use_id": None, "message": {"content": [
        {"type": "text", "text": "Earlier note: `xhigh effort` is discussed here."}]}})
    expect(readback(tmp, "standard", mention))
    # A recipe that names a target reviewed another scope than the bound current diff.
    expect(readback(tmp, "standard", standard_events(command="git diff origin/HEAD...HEAD"), target="-"),
           "recipe names a review target; current-diff readback expects none")
    for version, error in [("2.1.287", None), ("2.1.340+build.5", None), ("2.1.287-rc.0", "is not 2.1.287 or newer"),
                           ("2.1.300abc", "is not 2.1.287 or newer"), ("2.1.340-beta.1", None), ("2.1.200-rc.1", "is not 2.1.287 or newer"),
                           ("2.1.340.1", "is not 2.1.287 or newer"), ("v2.1.340", "is not 2.1.287 or newer")]:
        events = standard_events()
        events[0]["claude_code_version"] = version
        expect(readback(tmp, "standard", events), error)
    custom = custom_events()
    custom[0]["tools"].append("Task")
    expect(readback(tmp, "custom", custom, transcript()), "exceed the custom launch inventory")
    followup = as_followup(standard_events())
    followup[0]["permissionMode"] = "bypassPermissions"
    report = readback(tmp, "standard", standard_events(), followups=[followup])
    expect(report, "follow-up 1: init permissionMode 'bypassPermissions' is not dontAsk")
    assert report["followups"][0]["runtime"]["permission_mode"] == "bypassPermissions", report
    gap = standard_events(command="ls -la")
    gap[0]["claude_code_version"] = "2.1.200"
    report = readback(tmp, "standard", gap)
    assert "a --followup cannot clear" in report["problems"][-1], report

    events = standard_events()
    for event in events[2:4]:  # a verifier subagent's read reaches the verifier, not the reviewer
        event["parent_tool_use_id"] = "toolu_verifier"
    early = standard_events()
    early = [early[0], early[2], early[3], early[1], early[4]]
    stray = standard_events()
    stray[3]["parent_tool_use_id"] = "toolu_sub"
    report = readback(tmp, "standard", stray)
    expect(report, "did not reach the reviewer")
    assert report["diff_reads"][0]["reason"] == "result requested by a subagent, not the forked /review thread", report
    # Records split only at newlines: U+2028 appears unescaped inside a JSON string.
    separated = "".join(json.dumps(event, ensure_ascii=False) + "\n"
                        for event in standard_events(output=PATCH + "+line\u2028separator\n"))
    expect(readback(tmp, "standard", separated))
    main_thread = standard_events()
    for event in main_thread[2:4]:
        event["parent_tool_use_id"] = None
    report = readback(tmp, "standard", main_thread)
    assert report["diff_reads"][0]["reason"] == "requested by the main conversation, not the forked /review thread", report
    recipeless = standard_events()
    del recipeless[1]
    subagent = as_followup(standard_events())
    subagent[1]["parent_tool_use_id"] = subagent[2]["parent_tool_use_id"] = "toolu_sub"
    for stream, followups, reason in [
            (events, [], "requested by a subagent, not the forked /review thread"),
            (early, [], "requested before the /review recipe"), (recipeless, [], "no /review recipe precedes it"),
            (standard_events(command="ls -la"), [subagent], "requested by a subagent, not the resumed session")]:
        report = readback(tmp, "standard", stream, followups=followups)
        expect(report, "did not reach the reviewer" if stream is not recipeless else "no expanded /review recipe")
        assert [read["reason"] for read in report["diff_reads"]] == [reason], report
    events[2]["message"]["content"][0]["input"] = {"command": "git log -p"}
    report = readback(tmp, "standard", events)
    assert report["other_bash_requests"] == [{"tool_use_id": "diff-1", "command": "git log -p",
        "outside": "requested by a subagent, not the forked /review thread"}], report
    assert "resume the same session" in report["problems"][-1], report
    report = readback(tmp, "standard", standard_events(command="ls -la"), followups=[as_followup(standard_events())],
                      followup_prompts=[tmp / "missing-prompt.txt"])
    expect(report, "cannot read follow-up prompt")
    assert not any("cannot clear" in p for p in report["problems"]), report
    missing_events = subprocess.run([sys.executable, "-I", str(SCRIPT), "standard", str(tmp / "no-events.jsonl"), SID, MODEL,
                                     BASE, "high", str(tmp / "no-events.json")], capture_output=True, text=True)
    report = json.loads((tmp / "no-events.json").read_text(encoding="utf-8"))
    assert missing_events.returncode != 0 and report["problems"][-1] == "fix the EVENTS path and rerun readback", report
    assert not any("expected one init" in p or "resume" in p for p in report["problems"]), report
    # readback() writes every follow-up it is given, so call the helper directly with a missing path.
    (tmp / "gap.jsonl").write_text(json_lines(standard_events(command="ls -la")), encoding="utf-8")
    unreadable = subprocess.run([sys.executable, "-I", str(SCRIPT), "standard", str(tmp / "gap.jsonl"), SID, MODEL, BASE,
                                 "high", str(tmp / "gap.json"), "--followup", str(tmp / "missing-followup.jsonl")],
                                capture_output=True, text=True)
    report = json.loads((tmp / "gap.json").read_text(encoding="utf-8"))
    assert unreadable.returncode != 0 and "Traceback" not in unreadable.stderr, unreadable.stderr
    assert report["followups"] == [{"events": str(tmp / "missing-followup.jsonl"), "runtime": {}, "result": None,
                                    "permission_denials": [], "prompt_delivery": "unverified"}], report
    assert any(p.startswith("follow-up 1: cannot read follow-up events") for p in report["problems"]), report
    assert not any("cannot clear" in p or "expected one init" in p for p in report["problems"]), report
    assert any("fix its path and rerun readback before resuming" in p for p in report["problems"]), report
    (tmp / "corrupt-followup.jsonl").write_bytes(b"\xff\xfe not utf-8\n")
    subprocess.run([sys.executable, "-I", str(SCRIPT), "standard", str(tmp / "gap.jsonl"), SID, MODEL, BASE, "high",
                    str(tmp / "gap.json"), "--followup", str(tmp / "corrupt-followup.jsonl")], capture_output=True)
    report = json.loads((tmp / "gap.json").read_text(encoding="utf-8"))
    assert any(p.startswith("follow-up 1: cannot decode follow-up events") for p in report["problems"]), report
    assert any("cannot clear" in p for p in report["problems"]), report
    config = tmp / "unreadable-config"
    (config / "projects" / "-repo" / f"{SID}.jsonl").mkdir(parents=True)
    (tmp / "unreadable-prompt.txt").write_bytes(b"prompt")
    subprocess.run([sys.executable, "-I", str(SCRIPT), "standard", str(tmp / "gap.jsonl"), SID, MODEL, BASE, "high",
                    str(tmp / "unreadable.json"), "--followup", str(tmp / "gap.jsonl"), "--followup-prompt",
                    str(tmp / "unreadable-prompt.txt")], capture_output=True, env={**os.environ, "CLAUDE_CONFIG_DIR": str(config)})
    report = json.loads((tmp / "unreadable.json").read_text(encoding="utf-8"))
    assert any(p.startswith("cannot read transcript") for p in report["problems"]), report
    assert not any("session identity" in p for p in report["problems"]), report
    failed_followup = as_followup(standard_events(output="Exit code 128\nfatal: bad revision"))
    failed_followup[2]["message"]["content"][0]["is_error"] = True
    report = readback(tmp, "standard", standard_events(command="ls -la"), followups=[failed_followup],
                      followup_prompts=[b"prompt"])
    expect(report, "no transcript found")
    assert any("resume the same session" in p for p in report["problems"]), report
    assert not any("cannot clear" in p or "later typed transcript" in p for p in report["problems"]), report
    empty = tmp / "empty-reference.patch"
    empty.write_bytes(b"")
    report = readback(tmp, "standard", standard_events(command="ls -la"), reference_patch=empty)
    expect(report, "reference patch contains no patch text")
    assert any("resume the same session" in p for p in report["problems"]), report
    assert not any("cannot clear" in p for p in report["problems"]), report

    for fork, error in [(None, "None does not mark"), ("toolu_01", "'toolu_01' does not mark"),
                        ("forked-command-review", None)]:
        events = standard_events()
        for event in events[1:4]:  # the recipe and the reviewer's own calls share one thread
            event["parent_tool_use_id"] = fork
        report = readback(tmp, "standard", events)
        expect(report, error and "a prompt-started forked command")
        assert report["recipe_parent_tool_use_id"] == fork, report
        assert error is None or any(error in p for p in report["problems"]), report


def delivery_report(tmp):
    global checks
    first = "function admit(request) { return request.valid; }"
    second = "function retain(record, limit) { return record.size <= limit; }"
    # In a hunk, `---` is a removed line starting with `--`, not a file header.
    reference_text = (f"diff --git a/src/a.js b/src/a.js\n--- a/src/a.js\n+++ b/src/a.js\n@@ -1,3 +1,2 @@\n"
                      f"-{first.replace('valid', 'ok')}\n--- removed comment with leading dashes\n+{first}\n x\n"
                      f"diff --git a/src/b.js b/src/b.js\nnew file mode 100644\n--- /dev/null\n+++ b/src/b.js\n"
                      f"@@ -0,0 +1,3 @@\n+{second}\n+}}\n+-- comment that starts with two dashes --\n"
                      "diff --git a/img.png b/img.png\nBinary files a/img.png and b/img.png differ\n")
    reference = tmp / "delivery-reference.patch"
    reference.write_text(reference_text, encoding="utf-8")
    events = standard_events(command=f"git diff {BASE}..HEAD -- src/a.js",
                             output=f"diff --git a/src/a.js b/src/a.js\n@@ -1 +1 @@\n-{first.replace('valid', 'ok')}\n+{first}\n")
    report = readback(tmp, "standard", events, reference_patch=reference)
    expect(report)
    assert report["delivery"] == {"distinctive_min_chars": 12, "lines": 5, "delivered": 2,
        "files": [{"path": "src/a.js", "lines": 3, "delivered": 2}, {"path": "src/b.js", "lines": 2, "delivered": 0}],
        "unmeasured": ["img.png"]}, report
    # Read line numbers and grep prefixes are removed; follow-up streams count.
    followup = as_followup(standard_events(output=f"7\t{second}\nsrc/b.js:3:-- comment that starts with two dashes --\n"))
    followup[1]["message"]["content"][0].update(name="Read", input={"file_path": "/repo/src/b.js"})
    report = readback(tmp, "standard", events, followups=[followup], reference_patch=reference)
    assert report["delivery"]["delivered"] == 4 and report["delivery"]["files"][1]["delivered"] == 2, report
    assert report["ok"] and "delivery" not in " ".join(report["problems"]), report
    checks += 1
    odd = as_followup(standard_events(output='"x":1:foo "\ud83d":2:bar\n'))
    expect(readback(tmp, "standard", events, followups=[odd], reference_patch=reference))
    late = events + [
        {"type": "assistant", "parent_tool_use_id": FORK, "message": {"content": [{"type": "tool_use",
            "id": "late", "name": "Read", "input": {"file_path": "/repo/src/b.js"}}]}},
        {"type": "user", "parent_tool_use_id": FORK, "message": {"content": [{"type": "tool_result",
            "tool_use_id": "late", "content": f"1\t{second}\n"}]}}]
    report = readback(tmp, "standard", late, reference_patch=reference)
    expect(report)
    assert report["delivery"]["delivered"] == 2, report
    verifier = events[:-1] + [{**event, "parent_tool_use_id": "toolu_v"} for event in late[-2:]] + events[-1:]
    sub_followup = copy.deepcopy(followup)
    for event in sub_followup[1:3]:
        event["parent_tool_use_id"] = "toolu_sub"
    report = readback(tmp, "standard", verifier, followups=[sub_followup], reference_patch=reference)
    expect(report)
    assert report["delivery"]["delivered"] == 2, report
    assert "delivery" not in readback(tmp, "standard", events)
    held = readback(tmp, "standard", standard_events(command="ls -la", output=f"+{first}\n"), reference_patch=reference)
    expect(held, "no successful correlated")
    assert held["delivery"]["delivered"] == 1, held


def delivery_git_report(tmp):
    repo = tmp / "delivery-subject"
    repo.mkdir()
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}

    def git(*args):
        run = subprocess.run(["git", "-c", "core.hooksPath=" + os.devnull,
                              "-c", "commit.gpgsign=false", "-c", "core.quotePath=true",
                              "-c", "user.name=CC fixture", "-c", "user.email=cc-fixture@example.invalid", *args],
                             cwd=repo, env=env, capture_output=True, text=True)
        assert run.returncode == 0, run.stderr
        return run.stdout

    def write(name, content):
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content + "\n", encoding="utf-8")

    removed, renamed, binary = "folder b/deleted café.txt", "folder b/renamed.txt", "folder b/blob.bin"
    mode, empty = "mode-only.txt ", "empty.txt"
    links = {"type-long.txt": "long-symbolic-link-target", "type-short.txt": "x"}
    deleted_text = "deleted payload remains independently measurable"
    git("init", "-q")
    git("config", "diff.renames", "true")
    git("config", "core.filemode", "true")
    write(removed, deleted_text)
    write("a/foo.txt", "top-level a folder payload before the change")
    write(mode, "unchanged executable payload has no changed lines")
    write("old rename.txt", "unchanged rename payload remains independently identifiable")
    for name in links:
        write(name, f"regular-file contents before {name} becomes a symlink")
    (repo / binary).write_bytes(b"before\0binary\n")
    git("add", ".")
    git("commit", "-qm", "base")
    target = git("rev-parse", "HEAD").strip()

    separate = {"same.txt": "top-level payload is the only delivered file",
                "folder b/same.txt": "nested payload must remain visibly undelivered"}
    quoted = {"café.txt": "unicode filename retains its original identity",
              "tab\tname.txt": "tabbed filename retains its original identity",
              "back\\slash.txt": "backslash filename retains its original identity",
              "trailing.txt ": "trailing-space filename retains its original identity"}
    suffixes = {"grep suffix.txt": ["colon_suffix_must_remain_undelivered", "dash_suffix_must_remain_undelivered"]}
    grep_files = {name: [f"before_context_{index} keeps payload:42:{suffixes['grep suffix.txt'][0]}",
                         f"needle_match_{index} keeps payload-42-{suffixes['grep suffix.txt'][1]}",
                         f"after_context_{index} keeps payload:71:tail"]
                  for index, name in enumerate(("grep space.txt", "grep:17:field.txt", "grep-23-field.txt"))}
    ambiguous = {"ambiguity.txt": "prefix:42:ambiguous suffix remains uncredited",
                 "ambiguity.txt:1:prefix": "other ambiguity fixture remains undelivered"}
    # The source texts have 11, 12, and 13 non-whitespace characters. Internal
    # spaces and tabs must not turn an eleven-character line into a witness.
    boundary = {"short.txt": "abcdefghijk", "short-padded.txt": " a b\tc d e f\tg h i j k ",
                "twelve.txt": "abcdefghijkl", "twelve-padded.txt": " a b\tc d e f\tg h i j k l ",
                "thirteen.txt": "abcdefghijklm"}
    for name, content in {**separate, **quoted, **boundary, **ambiguous}.items():
        write(name, content)
    write("a/foo.txt", "top-level a folder payload after the change")
    write("docs/01-intro.md", "numbered chapter needle stays identifiable")
    write("dated.txt", "2024-01-01 release cutoff moved to the second quarter")
    write("schedule.txt", "12:30 standup moved to the afternoon block")
    write("b/new.txt", "top-level b folder payload is newly added")
    folders = ["a/foo.txt", "b/new.txt"]
    for name, lines in {**grep_files, **suffixes}.items():
        write(name, "\n".join(lines))
    invalid = os.fsdecode(b"invalid-\xff.txt")
    quoted[invalid] = "invalid-byte filename retains its original identity"
    (repo / empty).touch()
    (repo / mode).chmod(0o755)
    for name, destination in links.items():
        (repo / name).unlink()
        (repo / name).symlink_to(destination)
    (repo / removed).unlink()
    (repo / "old rename.txt").rename(repo / renamed)
    (repo / binary).write_bytes(b"after\0binary\n")
    git("add", "-A")
    # APFS rejects non-UTF-8 names, so the raw-byte path exists only in Git objects.
    blob = tmp / "invalid-blob"
    blob.write_text(quoted[invalid] + "\n", encoding="utf-8")
    git("update-index", "--add", "--cacheinfo", f"100644,{git('hash-object', '-w', str(blob)).strip()},{invalid}")
    git("commit", "-qm", "head")

    def observe(label, reference_paths, supplied_paths, followups=()):
        reference = tmp / f"delivery-{label}.patch"
        reference.write_text(git("diff", target, "HEAD", "--", *reference_paths), encoding="utf-8")
        args = ["diff", target, "HEAD", "--", *supplied_paths]
        events = standard_events(target=target, command=shlex.join(["git", *args]), output=git(*args))
        report = readback(tmp, "standard", events, target=target, reference_patch=reference,
                          followups=followups, cwd=repo)
        expect(report)
        return report["delivery"]

    def expected(files, unmeasured=()):
        return {"distinctive_min_chars": 12, "lines": sum(total for total, _ in files.values()),
                "delivered": sum(delivered for _, delivered in files.values()),
                "files": {name: {"lines": total, "delivered": delivered}
                          for name, (total, delivered) in files.items()}, "unmeasured": set(unmeasured)}

    def compare(actual, wanted):
        # A map makes Git's path ordering irrelevant, but must not hide duplicate
        # entries: every source file has exactly one independent delivery row.
        rows = actual["files"]
        assert len(rows) == len({row["path"] for row in rows}), actual
        normalized = {**actual, "files": {row["path"]: {k: v for k, v in row.items() if k != "path"}
                                          for row in rows}, "unmeasured": set(actual["unmeasured"])}
        assert normalized == wanted, (actual, wanted)

    compare(observe("separate", separate, ["same.txt"]),
            expected({name: (1, int(name == "same.txt")) for name in separate}))

    metadata = [*quoted, removed, "old rename.txt", renamed, binary, mode, empty]
    compare(observe("quoted-metadata", metadata, metadata),
            expected({name: (1, 1) for name in [*quoted, removed]}, [renamed, binary, mode, empty]))
    # A file-type change emits two Git sections for one canonical file. A short
    # symlink target must not put that measured file into unmeasured as well.
    compare(observe("type-changes", links, links),
            expected({"type-long.txt": (2, 2), "type-short.txt": (1, 1)}))
    quoted_args = ["grep", "--cached", "-n", "--full-name", "-e", "filename retains", "--", *quoted]
    quoted_followup = as_followup(standard_events(target=target, command=shlex.join(["git", *quoted_args]),
                                                  output=git(*quoted_args)))
    compare(observe("quoted-grep", quoted, ["same.txt"], [quoted_followup]),
            expected({name: (1, 1) for name in quoted}))

    # A real scoped diff supplies no grep-file content. The follow-up must account
    # for both ':' match lines and '-' context lines, without eating text suffixes.
    grep_args = ["grep", "-n", "-C1", "needle_match", "--", *grep_files]
    followup = as_followup(standard_events(target=target, command=shlex.join(["git", *grep_args]),
                                           output=git(*grep_args)))
    grep_reference = {**grep_files, **suffixes}
    compare(observe("grep-before", grep_reference, ["same.txt"]),
            expected({name: (len(lines), 0) for name, lines in grep_reference.items()}))
    compare(observe("grep-after", grep_reference, ["same.txt"], [followup]),
            expected({name: (len(lines), len(lines) if name in grep_files else 0)
                      for name, lines in grep_reference.items()}))
    # The Grep tool omits the path for a one-file search; absolute and ./ paths
    # come from searches rooted at the session directory.
    bare_args = ["grep", "-h", "-n", "-C1", "needle_match", "--", *grep_files]
    bare_output = git(*bare_args)
    assert bare_output.startswith("1-before_context_0"), bare_output
    bare_followup = as_followup(standard_events(target=target, command=shlex.join(["git", *bare_args]),
                                                output=bare_output))
    compare(observe("grep-bare", grep_reference, ["same.txt"], [bare_followup]),
            expected({name: (len(lines), len(lines) if name in grep_files else 0)
                      for name, lines in grep_reference.items()}))
    plain_args = ["grep", "-C1", "needle_match", "--", *grep_files]
    plain_output = git(*plain_args)
    assert plain_output.startswith("grep space.txt-before_context_0"), plain_output
    plain = as_followup(standard_events(target=target, command=shlex.join(["git", *plain_args]), output=plain_output))
    compare(observe("grep-unnumbered", grep_reference, ["same.txt"], [plain]),
            expected({name: (len(lines), len(lines) if name in grep_files else 0)
                      for name, lines in grep_reference.items()}))
    dated_args = ["grep", "-e", "release cutoff", "--", "dated.txt"]
    assert git(*dated_args).startswith("dated.txt:2024-01-01 release cutoff")
    dated = as_followup(standard_events(target=target, command=shlex.join(["git", *dated_args]), output=git(*dated_args)))
    compare(observe("grep-dated", ["dated.txt"], ["same.txt"], [dated]), expected({"dated.txt": (1, 1)}))
    timed_args = ["grep", "-e", "standup", "--", "schedule.txt"]
    assert git(*timed_args).startswith("schedule.txt:12:30 standup")
    timed = as_followup(standard_events(target=target, command=shlex.join(["git", *timed_args]), output=git(*timed_args)))
    compare(observe("grep-timed", ["schedule.txt"], ["same.txt"], [timed]), expected({"schedule.txt": (1, 1)}))
    rooted = "\n".join(prefix + line for prefix, line in zip((f"{repo}/", "./", f"{repo}/"),
                                                              git(*grep_args).split("\n")[:3]))
    rooted_followup = as_followup(standard_events(target=target, command="rg -n -C1 needle_match", output=rooted))
    rooted_followup[0]["cwd"] = str(repo)
    compare(observe("grep-rooted", grep_reference, ["same.txt"], [rooted_followup]),
            expected({name: (len(lines), len(lines) if name == "grep space.txt" else 0)
                      for name, lines in grep_reference.items()}))
    # A search from a subdirectory prints `01-intro.md:1:`, not the bare `1:` of a one-file search.
    nested_args = ["-C", "docs", "grep", "-n", "chapter needle"]
    assert git(*nested_args).startswith("01-intro.md:1:")
    nested = as_followup(standard_events(target=target, command=shlex.join(["git", *nested_args]),
                                         output=git(*nested_args)))
    compare(observe("grep-nested", ["docs/01-intro.md"], ["same.txt"], [nested]),
            expected({"docs/01-intro.md": (1, 1)}))
    ambiguous_args = ["grep", "-n", "-e", "prefix", "--", "ambiguity.txt"]
    ambiguous_followup = as_followup(standard_events(target=target,
        command=shlex.join(["git", *ambiguous_args]), output=git(*ambiguous_args)))
    compare(observe("ambiguous-grep", ambiguous, ["same.txt"], [ambiguous_followup]),
            expected({name: (1, 0) for name in ambiguous}))

    compare(observe("prefix-folders", folders, folders), expected({"a/foo.txt": (2, 2), "b/new.txt": (1, 1)}))
    compare(observe("boundaries", boundary, boundary),
            expected({name: (1, 1) for name in ("twelve.txt", "twelve-padded.txt", "thirteen.txt")},
                     ["short.txt", "short-padded.txt"]))

    # The reference is captured under the reviewer's Git configuration, so a
    # semicolon-hidden read still matches it byte for byte; delivery decodes
    # diff.noprefix paths and retains other prefixes as unparsed sections.
    git("config", "diff.noprefix", "true")
    assert git("diff", target, "HEAD", "--", "same.txt").startswith("diff --git same.txt same.txt\n")
    compare(observe("no-prefix-config", separate, ["same.txt"]),
            expected({name: (1, int(name == "same.txt")) for name in separate}))
    compare(observe("no-prefix-folders", folders, folders), expected({"a/foo.txt": (2, 2), "b/new.txt": (1, 1)}))
    reference = tmp / "delivery-semicolon.patch"
    reference.write_text(git("diff", f"{target}..HEAD", "--"), encoding="utf-8")
    hidden = standard_events(target=f"{target}..HEAD", command=f"git diff {target}..HEAD; git status --short",
                             output=git("diff", f"{target}..HEAD") + "\n")
    report = readback(tmp, "standard", hidden, target=f"{target}..HEAD", reference_patch=reference, cwd=repo)
    expect(report)
    assert report["diff_reads"][0].get("reference_matched"), report
    git("config", "diff.noprefix", "false")
    git("config", "diff.srcPrefix", "old/")
    git("config", "diff.dstPrefix", "new/")
    assert git("diff", target, "HEAD", "--", "same.txt").startswith("diff --git old/same.txt new/same.txt\n")
    unknown = observe("custom-prefix-config", ["same.txt"], ["same.txt"])
    header = (tmp / "delivery-custom-prefix-config.patch").read_text(encoding="utf-8").split("\n", 1)[0]
    compare(unknown, {**expected({}), "unparsed_headers": [header]})


def main():
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        target, patch, failed, changed, scoped = git_observations(tmp)
        events = standard_events(target=target, command=f"git diff {target} HEAD", output=patch.stdout)
        report = readback(tmp, "standard", events, target=target)
        expect(report)
        assert report["diff_reads"][0]["ok"] and report["result"] == "(none)"
        expect(readback(tmp, "standard", standard_events(target=target,
            command=f"git diff --unified=20 {target} HEAD -- check.txt", output=scoped.stdout), target=target))

        failure = standard_events(target=target, command=f"git diff {target}",
                                  output=f"Exit code {failed.returncode}\n{failed.stderr}")
        failure[3]["message"]["content"][0]["is_error"] = True
        expect(readback(tmp, "standard", failure, target=target), "no successful correlated")
        # Terminal success and a false is_error flag cannot erase explicit Git failure.
        failure[3]["message"]["content"][0]["is_error"] = False
        expect(readback(tmp, "standard", failure, target=target), "no successful correlated")
        recovered = copy.deepcopy(failure)
        retry = copy.deepcopy(events[2:4])
        retry[0]["message"]["content"][0]["id"] = "diff-2"
        retry[1]["message"]["content"][0]["tool_use_id"] = "diff-2"
        recovered[4:4] = retry
        report = readback(tmp, "standard", recovered, target=target)
        expect(report)
        assert [read["ok"] for read in report["diff_reads"]] == [False, True]
        exit_one = standard_events(target=target, command=f"git diff --exit-code {target} HEAD",
                                   output=f"Exit code 1\n{changed.stdout}")
        exit_one[3]["message"]["content"][0]["is_error"] = True
        expect(readback(tmp, "standard", exit_one, target=target))
        exit_one[2]["message"]["content"][0]["input"]["command"] = f"git diff {target} HEAD -- --exit-code"
        expect(readback(tmp, "standard", exit_one, target=target), "no successful correlated")

        for result in ["Reviewed the full changeset and its callers. No findings.",
                       "check.txt:1 — invalid inputs are accepted.\nsecond.py:4 — valid entries are dropped.\n"]:
            report = readback(tmp, "standard", standard_events(result=result))
            expect(report)
            assert report["result"] == result and "findings" not in report
        for result in ["", None, {}]:
            expect(readback(tmp, "standard", standard_events(result=result)), "no nonempty native result")
        for command in [f"git diff {BASE}", f"git diff {BASE}..HEAD", f"git diff {BASE}...HEAD",
                        f"git --no-pager diff --no-ext-diff --no-textconv {BASE} HEAD --",
                        f"git diff --unified=20 {BASE} HEAD", f"git diff -U20 {BASE} HEAD",
                        f"git diff --unified --color=never {BASE} HEAD",
                        f"git diff -U {BASE} HEAD -- check.txt", f"git diff {BASE} HEAD -- check.txt"]:
            expect(readback(tmp, "standard", standard_events(command=command)))
        for command in ["git status", f"git diff {'f' * 40} HEAD", f"git diff {BASE} {'b' * 40}",
                        f"git diff --stat {BASE} HEAD", f"git diff --unified=bad {BASE} HEAD",
                        f"git diff --unified 20 {BASE} HEAD", f"git diff -U 20 {BASE} HEAD",
                        f"git diff HEAD -- {BASE}",
                        f"echo 'git diff {BASE} HEAD'", f"git diff {BASE} HEAD; true"]:
            expect(readback(tmp, "standard", standard_events(command=command)), "no successful correlated")

        # Only the final && group is established by successful compound completion.
        stat = " check.txt | 2 +-\n 1 file changed, 1 insertion(+), 1 deletion(-)\n"
        for command, output in [
            (f"git diff {target} && git diff HEAD", patch.stdout),
            (f"git diff {target} HEAD --stat && git diff {target} HEAD && ls -a && "
             "find . -name CLAUDE.md -not -path './.git/*'", stat + patch.stdout + ".\n..\ncheck.txt\n"),
            (f"git diff {target[:7]} HEAD --stat && git diff {target[:7]} HEAD && git status --short && ls -la",
             stat + patch.stdout + "total 8\n"),
        ]:
            report = readback(tmp, "standard", standard_events(target=target, command=command, output=output),
                              target=target)
            expect(report)
            assert report["diff_reads"][0]["shape"] == "chain", report
        # The launch passes a range target; the recipe names it and the reviewer diffs it (observed live).
        span = f"{target}..HEAD"
        report = readback(tmp, "standard", standard_events(
            target=span, command=f"git diff {span}; git diff HEAD", output=patch.stdout), target=span)
        expect(report, "no successful correlated")
        assert report["diff_reads"][0]["shape"] == "chain", report
        # Observed live with a bare-SHA target: the reviewer showed that one commit instead.
        expect(readback(tmp, "standard", standard_events(
            target=target, command=f"git show {target} --stat && git show {target} | head -400",
            output=patch.stdout), target=target), "no successful correlated")
        # Patch text cannot restore a status discarded by a semicolon.
        report = readback(tmp, "standard", standard_events(
            target=target, command=f"git diff {target}; git diff HEAD", output="fatal: bad revision\n"), target=target)
        expect(report, "no successful correlated")
        assert "completion status is unavailable" in report["diff_reads"][0]["reason"]
        # Rejected by shape even though the output below carries patch text.
        for command in [f"git diff {BASE} HEAD; git show HEAD", f"git diff {BASE} HEAD; echo 'diff --git a/x b/x'",
                        f"git diff {BASE} HEAD | head -50", f"git diff {BASE} HEAD && rm -rf build",
                        f"git diff --stat {BASE} HEAD; git status", "git diff HEAD; ls",
                        f"git diff {BASE} HEAD; find . -exec cat {{}} +", f"git diff {BASE} HEAD; git status -v",
                        f"git diff {BASE} HEAD &", f"git diff {BASE} HEAD || true", f"git diff {BASE} HEAD 2>&1",
                        f"git diff {BASE} HEAD; git diff --stat -p {BASE} HEAD", f"git diff {BASE} HEAD; ; ls"]:
            expect(readback(tmp, "standard", standard_events(command=command)), "no successful correlated")
        expect(readback(tmp, "standard", standard_events(level="medium")), "recipe ran at medium")

        missing = standard_events()
        del missing[3]
        expect(readback(tmp, "standard", missing), "no successful correlated")
        wrong_id = standard_events()
        wrong_id[3]["message"]["content"][0]["tool_use_id"] = "another-command"
        expect(readback(tmp, "standard", wrong_id), "no successful correlated")
        no_id = standard_events()
        del no_id[2]["message"]["content"][0]["id"]
        expect(readback(tmp, "standard", no_id), "no successful correlated")
        duplicate = standard_events()
        duplicate.insert(3, copy.deepcopy(duplicate[2]))
        expect(readback(tmp, "standard", duplicate), "no successful correlated")
        out_of_order = standard_events()
        out_of_order[2], out_of_order[3] = out_of_order[3], out_of_order[2]
        expect(readback(tmp, "standard", out_of_order), "no successful correlated")
        after_terminal = standard_events()
        after_terminal[3], after_terminal[4] = after_terminal[4], after_terminal[3]
        expect(readback(tmp, "standard", after_terminal), "no successful correlated")
        background = standard_events(output="Command running in background with ID: task-1")
        expect(readback(tmp, "standard", background), "no successful correlated")
        background = standard_events()
        background[2]["message"]["content"][0]["input"]["run_in_background"] = True
        expect(readback(tmp, "standard", background), "no successful correlated")
        # Bash metadata appears on main-conversation results, so exercise it in a follow-up.
        for details in [{"backgroundTaskId": "task-1"}, {"interrupted": True}, {"exitCode": 129}]:
            original = standard_events()
            original[3]["tool_use_result"] = details
            expect(readback(tmp, "standard", original), "no successful correlated")
            followup = as_followup(standard_events())
            followup[2]["tool_use_result"].update(details)
            expect(readback(tmp, "standard", standard_events(command="ls -la"), followups=[followup]),
                   "no successful correlated")

        denial = [{"tool_name": "Bash", "tool_input": {"command": "npm test"}}]
        denied = standard_events()
        denied[-1]["permission_denials"] = denial
        report = readback(tmp, "standard", denied)
        expect(report)
        assert report["permission_denials"] == denial
        del denied[3]
        report = readback(tmp, "standard", denied)
        expect(report, "no successful correlated")
        assert report["permission_denials"] == denial

        for where, key, value, error in [
            (0, "session_id", "other", "init session"),
            (-1, "session_id", "other", "result session"),
            (0, "model", "other-model", "init model"),
            (-1, "modelUsage", {MODEL: {}, "other-model": {}}, "models used"),
            (-1, "subtype", "error_during_execution", "result is error_during_execution"),
            (-1, "permission_denials", {}, "permission_denials is not an array"),
        ]:
            events = standard_events()
            events[where][key] = value
            expect(readback(tmp, "standard", events), error)
        expect(readback(tmp, "standard", standard_events()[:-1]), "not terminal")
        expect(readback(tmp, "standard", standard_events() + [standard_events()[-1]]), "expected one terminal result")
        expect(readback(tmp, "standard", "{bad JSON\n" + json_lines(standard_events())), "invalid JSON")
        expect(readback(tmp, "standard", [None] + standard_events()), "expected an object")
        malformed = standard_events()
        malformed[2]["message"] = None
        expect(readback(tmp, "standard", malformed), "no successful correlated")

        expect(readback(tmp, "custom", custom_events(), transcript()))
        ask = b"Reassess finding 2 against check.txt.\n"
        typed = transcript() + [{"type": "user", "isSidechain": True, "sessionId": SID, "message": {"content": "sub"}},
                                {"type": "user", "sessionId": SID, "message": {"content": ask.decode()}}, reply("msg-a")]
        first = answered(custom_events(), "msg-a")
        report = readback(tmp, "custom", custom_events(), typed, followups=[first], followup_prompts=[ask])
        expect(report)
        assert report["followups"][0]["prompt_delivery"] == "verified", report
        for records, prompts in [(transcript(), [ask]), (typed, [ask + b" "])]:
            expect(readback(tmp, "custom", custom_events(), records, followups=[first],
                            followup_prompts=prompts), "follow-up 1: the follow-up prompt is not a later typed transcript message")
        standard_typed = [{"type": "user", "sessionId": SID, "message": {"content": "/review high x..HEAD"}},
                          {"type": "user", "sessionId": SID, "message": {"content": [{"type": "tool_result"}]}},
                          {"type": "user", "sessionId": SID, "message": {"content": ask.decode()}}, reply("msg-a")]
        report = readback(tmp, "standard", standard_events(command="ls -la"), standard_typed,
                          followups=[answered(as_followup(standard_events()), "msg-a")], followup_prompts=[ask])
        expect(report)
        assert report["followups"][0]["prompt_delivery"] == "verified", report
        assert report["transcript"].endswith(f"{SID}.jsonl"), report  # the evidence names its transcript
        summary = {"type": "user", "sessionId": SID, "isCompactSummary": True, "isVisibleInTranscriptOnly": True,
                   "message": {"content": "This session is being continued from a previous conversation."}}
        report = readback(tmp, "standard", standard_events(command="ls -la"), standard_typed[:-1] + [summary, reply("msg-a")],
                          followups=[answered(as_followup(standard_events()), "msg-a")], followup_prompts=[ask])
        expect(report)  # compaction between a prompt and its answer does not take the answer slot
        # The first reply after a prompt is its answer even when that reply's id is malformed.
        malformed_first = standard_typed[:-1] + [{"type": "assistant", "sessionId": SID, "message": {"id": [1]}},
                                                 reply("msg-a")]
        expect(readback(tmp, "standard", standard_events(), malformed_first,
                        followups=[answered(as_followup(standard_events()), "msg-a")], followup_prompts=[ask]),
               "answered by this stream")
        odd_id = answered(as_followup(standard_events()), "msg-a")
        odd_id[-2]["message"]["id"] = [1]
        expect(readback(tmp, "standard", standard_events(), standard_typed, followups=[odd_id], followup_prompts=[ask]),
               "answered by this stream")
        # A prompt verified for another resume's stream is not this stream's delivery.
        expect(readback(tmp, "standard", standard_events(), standard_typed,
                        followups=[answered(as_followup(standard_events()), "msg-b")], followup_prompts=[ask]),
               "answered by this stream: delivery unverified")
        report = readback(tmp, "standard", standard_events(), followups=[as_followup(standard_events())])
        expect(report)
        assert report["followups"][0]["prompt_delivery"] == "unverified", report
        ask2 = b"Now reassess finding 3.\n"
        compacted = typed + [{"type": "user", "sessionId": SID, "isCompactSummary": True, "isVisibleInTranscriptOnly": True,
                              "message": {"content": "This session is being continued from a previous conversation."}},
                             {"type": "user", "sessionId": SID, "message": {"content": [{"type": "text", "text": ask2.decode()}]}},
                             reply("msg-b")]
        second = answered(custom_events(), "msg-b")
        report = readback(tmp, "custom", custom_events(), compacted, followups=[first, second], followup_prompts=[ask, ask2])
        expect(report)
        assert [entry["prompt_delivery"] for entry in report["followups"]] == ["verified", "verified"], report
        expect(readback(tmp, "custom", custom_events(), compacted, followups=[first, second],
                        followup_prompts=[ask2, ask]), "follow-up 1: the follow-up prompt is not a later typed")
        expect(readback(tmp, "custom", custom_events(), compacted, followups=[second], followup_prompts=[ask]),
               "follow-up 1: the follow-up prompt is not a later typed transcript message answered by this stream")
        report = readback(tmp, "standard", standard_events(command="ls -la"), standard_typed, extra_transcript=True,
                          followups=[answered(as_followup(standard_events()), "msg-a")], followup_prompts=[ask])
        expect(report, "multiple transcripts")
        # One bad transcript line is a session problem; the rest still verifies delivery.
        damaged = readback(tmp, "custom", custom_events(), json_lines(typed) + "{bad JSON\n", followups=[first],
                           followup_prompts=[ask])
        expect(damaged, "invalid JSON")
        assert "transcript" in damaged and damaged["followups"][0]["prompt_delivery"] == "verified", damaged
        foreign = standard_typed + [{"type": "user", "sessionId": "other", "message": {"content": "x"}}]
        expect(readback(tmp, "standard", standard_events(), foreign,
                        followups=[answered(as_followup(standard_events()), "msg-a")], followup_prompts=[ask]),
               "transcript mixes sessions")
        report = readback(tmp, "custom", custom_events(), None, followups=[custom_events()], followup_prompts=[ask])
        assert sum("no transcript found" in p for p in report["problems"]) == 1, report  # one transcript reader
        malformed = [{"type": "user", "sessionId": SID, "message": "not an object"}] + transcript()[1:]
        expect(readback(tmp, "custom", custom_events(), malformed), "first transcript message is not the exact prompt")
        surrogate = [{"type": "user", "sessionId": SID, "message": {"content": "\ud83d prompt"}}]
        expect(readback(tmp, "custom", custom_events(), surrogate), "first transcript message is not the exact prompt")
        unpaired = subprocess.run([sys.executable, "-I", str(SCRIPT), "standard", "events", SID, MODEL, BASE, "high",
                                   "out", "--followup", "a", "--followup", "b", "--followup-prompt", "p"],
                                  capture_output=True, text=True)
        assert unpaired.returncode != 0 and "usage:" in unpaired.stderr
        report = readback(tmp, "custom", custom_events(), transcript(), followups=[custom_events()])
        expect(report)
        assert report["followups"][0]["structured_output"] == custom_events()[-1]["structured_output"], report
        missing = custom_events()
        del missing[-1]["structured_output"]
        expect(readback(tmp, "custom", custom_events(), transcript(), followups=[missing]),
               "follow-up 1: no follow-up structured_output object")
        expect(readback(tmp, "custom", custom_events(), transcript(), followups=[standard_events()]),
               "follow-up 1: init tools")
        expect(readback(tmp, "custom", custom_events(), transcript(PROMPT + b" ")), "delivery unverified")
        missing = custom_events()
        del missing[-1]["structured_output"]
        expect(readback(tmp, "custom", missing, transcript()), "no structured_output")
        expect(readback(tmp, "custom", custom_events()), "no transcript found")
        expect(readback(tmp, "custom", custom_events(), transcript(), extra_transcript=True), "multiple transcripts")
        mixed = transcript() + [{"type": "user", "sessionId": "other", "message": {"content": "x"}}]
        expect(readback(tmp, "custom", custom_events(), mixed), "transcript mixes sessions")
        expect(readback(tmp, "custom", custom_events(), "{bad JSON\n"), "invalid JSON")
        denied = custom_events()
        denied[-1]["permission_denials"] = denial
        report = readback(tmp, "custom", denied, transcript())
        expect(report)
        assert report["permission_denials"] == denial

        launch_effort(tmp)
        chain_checks(tmp)
        reference_boundary(tmp)
        inquiry_diagnostics(tmp)
        terminal_evidence(tmp)
        persisted_reads(tmp)
        runtime_evidence(tmp)
        delivery_report(tmp)
        delivery_git_report(tmp)

    print(f"cc: {checks} readback and launch checks passed, including real Git and conflicting effort environments; no model was called")


if __name__ == "__main__":
    main()

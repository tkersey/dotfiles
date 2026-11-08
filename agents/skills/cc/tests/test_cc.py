"""Offline cc readback checks, including real Git results; no model is called.

usage: uv run --no-project python -I agents/skills/cc/tests/test_cc.py
"""

import copy
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "readback.py"
SID = "11111111-2222-4333-8444-555555555555"
MODEL = "claude-opus-5-5"
BASE = "04c0a84a962c3e637c14614498aa1950a776ba6e"
PROMPT = b"Perform one independent, read-only code review.\n\n{\"lens_name\": \"fresh-eyes\"}"
PATCH = "diff --git a/check.txt b/check.txt\n@@ -1 +1 @@\n-before\n+after\n"
checks = 0


def standard_events(level="high", target=BASE, command=None, output=PATCH, result="(none)"):
    return [
        {"type": "system", "subtype": "init", "session_id": SID, "model": MODEL},
        {"type": "user", "message": {"content": [{"type": "text", "text":
            f"Review target: `{target}`\n\n`{level} effort → 8 inline angles → ≤10 findings`\n\n## Phase 1"}]}},
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "diff-1", "name": "Bash",
            "input": {"command": command or f"git diff {target[:12]} HEAD"}}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "diff-1",
            "is_error": False, "content": output}]}},
        {"type": "result", "subtype": "success", "is_error": False, "session_id": SID,
         "modelUsage": {MODEL: {}}, "permission_denials": [], "result": result},
    ]


def custom_events():
    output = {"findings": [], "overall_correctness": "patch is correct",
              "overall_explanation": "Inspected the whole changeset.", "overall_confidence_score": 0.8}
    return [
        {"type": "system", "subtype": "init", "session_id": SID, "model": MODEL},
        {"type": "result", "subtype": "success", "is_error": False, "session_id": SID,
         "modelUsage": {MODEL: {}}, "permission_denials": [], "result": "", "structured_output": output},
    ]


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
             followups=()):
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
    for index, stream in enumerate(followups):
        path = tmp / f"followup-{index}.jsonl"
        path.write_text(json_lines(stream), encoding="utf-8")
        args.extend(["--followup", str(path)])
    # sys.executable is the interpreter selected by the outer UV invocation.
    proc = subprocess.run([sys.executable, "-I", str(SCRIPT), *args],
                          env={**os.environ, "CLAUDE_CONFIG_DIR": str(config)}, capture_output=True, text=True)
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
printf 'environment=%s\\nlocks=%s\\n' "$CLAUDE_CODE_EFFORT_LEVEL" "$GIT_OPTIONAL_LOCKS"
while (($#)); do
  if [[ "$1" == "--effort" ]]; then printf 'flag=%s\\n' "$2"; fi
  shift
done
''')
    stub.chmod(0o755)
    repo = tmp / "launch subject with spaces"
    repo.mkdir()
    prompt = tmp / "launch prompt with spaces"
    prompt.write_bytes(PROMPT)
    settings = tmp / "launch-settings.json"
    settings.write_text("{}\n")
    for kind, command in [("standard", standard), ("custom", custom)]:
        for selected, inherited in [("high", "low"), ("low", "max")]:
            events = tmp / f"launch-{kind}-{selected}.jsonl"
            env = {**os.environ, "PATH": str(binary) + os.pathsep + os.environ["PATH"],
                   "CLAUDE_CODE_EFFORT_LEVEL": inherited, "selected_effort": selected,
                   "repo": str(repo), "selected_model": MODEL, "level": "high", "base": BASE,
                   "settings": str(settings), "events": str(events),
                   "diagnostics": str(tmp / "launch-errors"), "prompt": str(prompt), "skill_dir": str(skill)}
            script = f"uuidgen() {{ printf '%s\\n' '{SID}'; }}\n" + setup + "\n" + command
            run = subprocess.run(["bash", "-eu", "-c", script], env=env, capture_output=True, text=True)
            assert run.returncode == 0, run.stderr
            observed = dict(line.split("=", 1) for line in events.read_text().splitlines())
            assert observed == {"environment": selected, "locks": "0", "flag": selected}, observed
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
                    f"git diff {target} --stat && git diff {target} && git status --short && ls -la",
                    f"git diff {target} -- 'literal;path' 'literal&&path'"]:
        events, run = observation(command)
        assert run.returncode == 0
        expect(readback(tmp, "standard", events, target=target))

    original, run = observation(f"git diff {target}; git diff HEAD")
    assert run.returncode == 0 and "diff --git" in run.stdout
    report = readback(tmp, "standard", original, target=target)
    expect(report, "no successful correlated")
    assert "completion status is unavailable" in report["diff_reads"][0]["reason"]
    supplemental, _ = observation(f"git diff {target}")
    del supplemental[1]
    supplemental[1]["message"]["content"][0]["id"] = "diff-2"
    supplemental[2]["message"]["content"][0]["tool_use_id"] = "diff-2"
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
        for details in [{"backgroundTaskId": "task-1"}, {"interrupted": True}, {"exitCode": 129}]:
            events = standard_events()
            events[3]["tool_use_result"] = details
            expect(readback(tmp, "standard", events), "no successful correlated")

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
        expect(readback(tmp, "custom", custom_events(), transcript(PROMPT + b" ")), "delivery unverified")
        missing = custom_events()
        del missing[-1]["structured_output"]
        expect(readback(tmp, "custom", missing, transcript()), "no structured_output")
        expect(readback(tmp, "custom", custom_events()), "no unique transcript")
        expect(readback(tmp, "custom", custom_events(), transcript(), extra_transcript=True), "no unique transcript")
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

    print(f"cc: {checks} readback and launch checks passed, including real Git and conflicting effort environments; no model was called")


if __name__ == "__main__":
    main()

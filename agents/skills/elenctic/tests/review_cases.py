#!/usr/bin/env python3
"""Offline review subjects, evaluator-only probes, and unmodified report capture.

These small discriminators qualify fixture behavior and export isolation, not
model efficacy. Follow validation.md; never give this utility or its key to a reviewer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import secrets
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path


def source(value: str) -> str:
    return textwrap.dedent(value).strip() + "\n"


@dataclass(frozen=True)
class Pair:
    name: str
    requirements: str
    base: dict[str, str]
    candidate: dict[str, str]
    change: tuple[str, str, str]
    probe: str
    basis: str
    discussion: str = ""

    def files(self, variant: str) -> dict[str, str]:
        files = dict(self.candidate)
        if variant == "defective":
            path, before, after = self.change
            if files[path].count(before) != 1:
                raise ValueError(f"ambiguous fixture edit: {self.name}")
            files[path] = files[path].replace(before, after)
        elif variant != "adequate":
            raise ValueError("unknown variant")
        return files


PAIRS: list[Pair] = []

submission = source('''
    class Submission:
        def __init__(self, entries):
            items = list(entries)
            if not items:
                raise ValueError("empty submission")
            self._items = items

        def first(self):
            return self._items[0]

        def entries(self):
            return list(self._items)
''')
PAIRS.append(Pair(
    "retained-guarantee",
    "Submission accepts sequences of strings and records a nonempty snapshot at construction. Callers may reuse their input buffers. "
    "first() and entries() observe that snapshot; entries() returns caller-owned data.",
    {"submission.py": submission.replace("items = list(entries)", "items = tuple(entries)")},
    {"submission.py": submission},
    ("submission.py", "items = list(entries)", "items = entries if isinstance(entries, list) else list(entries)"),
    source('''
        from submission import Submission
        entries = ["a", "b"]
        item = Submission(entries)
        entries.clear()
        try:
            observed = [item.first(), item.entries()]
        except IndexError:
            observed = "IndexError"
        copy = Submission(["c"])
        copy.entries().clear()
        return {"passes": observed == ["a", ["a", "b"]] and copy.first() == "c", "observed": observed}
    '''),
    "Caller buffer reuse invalidates the promised snapshot; copying closes the alias without a stronger public type.",
))

vault = source('''
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Handle:
        document: str
        user: str
        expires: int

    class Vault:
        def __init__(self):
            self.documents = {"guide": "content"}
            self.grants = {"guide": {"lee"}}

        def open(self, document, user, now):
            if user not in self.grants[document]:
                raise PermissionError(user)
            return Handle(document, user, now + 60)

        def revoke(self, document, user):
            self.grants[document].discard(user)

        def read(self, handle, now):
            if now >= handle.expires or handle.user not in self.grants[handle.document]:
                raise PermissionError(handle.user)
            return self.documents[handle.document]
''')
PAIRS.append(Pair(
    "temporal-facts",
    "Vault handles now expire 60 time units after opening. Revocation takes effect on the next read, "
    "including reads through existing handles. Opening a handle does not deliver document content.",
    {"vault.py": vault.replace("now >= handle.expires or ", "")},
    {"vault.py": vault},
    ("vault.py", "now >= handle.expires or handle.user not in self.grants[handle.document]", "now >= handle.expires"),
    source('''
        from vault import Vault
        vault = Vault()
        handle = vault.open("guide", "lee", 0)
        initial = vault.read(handle, 1)
        vault.revoke("guide", "lee")
        try:
            after = vault.read(handle, 2)
        except PermissionError:
            after = "denied"
        other = Vault()
        try:
            other.read(other.open("guide", "lee", 0), 60)
            expired = False
        except PermissionError:
            expired = True
        return {"passes": initial == "content" and after == "denied" and expired, "observed": after}
    '''),
    "A handle's unexpired admission does not establish continued permission; the adequate variant keeps both distinct checks.",
))

engine = source('''
    from collections import deque

    class Engine:
        def __init__(self, execute):
            self.execute = execute
            self.ready = deque()
            self.waiting = {}
            self.states = {}

        def submit(self, job):
            self.states[job] = "ready"
            self.ready.append(job)

        def tick(self, now):
            for job, due in list(self.waiting.items()):
                if due <= now:
                    del self.waiting[job]
                    self.states[job] = "ready"
                    self.ready.append(job)
            if not self.ready:
                return
            job = self.ready.popleft()
            if self.execute(job) == "retry":
                self.states[job] = "waiting"
                self.waiting[job] = now + 5
            else:
                self.states[job] = "done"
''')
PAIRS.append(Pair(
    "liveness",
    "Each submitted job ID is unique. execute returns either retry or done. Retries wait five time units. "
    "Ticks continue at unbounded increasing integer times, and execute eventually returns done. Accepted jobs must finish; "
    "ready, waiting, and done are the supported states.",
    {"engine.py": engine.replace("self.waiting[job] = now + 5", "self.waiting[job] = now")},
    {"engine.py": engine},
    ("engine.py", '                self.ready.append(job)\n', ""),
    source('''
        from engine import Engine
        calls = []
        def execute(job):
            calls.append(job)
            return "retry" if len(calls) == 1 else "done"
        engine = Engine(execute)
        engine.submit("j")
        engine.tick(0)
        engine.tick(4)
        early = len(calls)
        engine.tick(5)
        engine.tick(6)
        return {"passes": early == 1 and calls == ["j", "j"] and engine.states["j"] == "done",
                "observed": {"calls": calls, "state": engine.states["j"]}}
    '''),
    "A due retry is marked ready without becoming runnable. All state labels remain valid while required progress fails.",
))

storage = source('''
    class Storage:
        def __init__(self):
            self.tables = {}

        def for_tenant(self, tenant):
            return self.tables.setdefault(tenant, {})
''')
reader = source('''
    from keys import account_key

    def read_account(storage, backend, tenant, account):
        table = storage.for_tenant(tenant)
        key = account_key(tenant, account)
        if key not in table:
            table[key] = backend(tenant, account)
        return table[key]
''')
PAIRS.append(Pair(
    "unchanged-adapter",
    "read_account returns the backend's account for the requested tenant and account ID. "
    "One Storage instance may serve multiple tenants. Repeated requests may be cached.",
    {"keys.py": "def account_key(tenant, account):\n    return tenant, account\n", "storage.py": storage, "reader.py": reader},
    {"keys.py": "def account_key(tenant, account):\n    return account\n", "storage.py": storage, "reader.py": reader},
    ("storage.py", "self.tables.setdefault(tenant, {})", 'self.tables.setdefault("accounts", {})'),
    source('''
        from storage import Storage
        from reader import read_account
        storage = Storage()
        backend = lambda tenant, account: tenant + ":" + account
        observed = [read_account(storage, backend, tenant, "17") for tenant in ["a", "b", "a"]]
        return {"passes": observed == ["a:17", "b:17", "a:17"], "observed": observed}
    '''),
    "Key and ownership changes compose through the unchanged reader. Tenant-local ownership makes the same key change adequate.",
))

formatter = source(r'''
    def cell(value):
        if any(ch in value for ch in ',"\n'):
            return '"' + value.replace('"', '""') + '"'
        return value
''')
csv_test = source('''
    from formatter import cell

    def test_cell():
        value = 'a,"b"'
        expected = '"a,""b"""'
        assert cell(value) == expected
''')
PAIRS.append(Pair(
    "test-authority",
    "cell emits a CSV field: fields containing a comma, quote, or newline are quoted, and embedded "
    "quotes are doubled. This change adds regression coverage for quoted fields. The current formatter is otherwise unchanged.",
    {"formatter.py": formatter},
    {"formatter.py": formatter, "test_csv.py": csv_test},
    ("test_csv.py", "expected = '\"a,\"\"b\"\"\"'", "expected = cell(value)"),
    source('''
        import runpy
        import formatter
        runpy.run_path("test_csv.py")["test_cell"]()
        formatter.cell = lambda value: value
        try:
            runpy.run_path("test_csv.py")["test_cell"]()
            rejects = False
        except AssertionError:
            rejects = True
        return {"passes": rejects, "observed": {"rejects_unquoted_output": rejects}}
    '''),
    "The new assertion's expected result repeats the producer under test and accepts unquoted output. This is a test-quality witness, not an observed production failure.",
))

gateway = source('''
    class Gateway:
        def __init__(self):
            self.deliveries = []

        def send(self, payload, preview=False):
            if not preview:
                self.deliveries.append(payload)
            return payload
''')
service = source('''
    class Service:
        def __init__(self, gateway):
            self.gateway = gateway
            self.pending = []

        def submit(self, payload, preview=False, defer=False):
            normalized = payload.strip()
            if defer:
                self.pending.append({"payload": normalized, "preview": preview})
                return normalized
            return self.gateway.send(normalized, preview=preview)

        def drain(self):
            while self.pending:
                item = self.pending.pop(0)
                self.gateway.send(item["payload"], preview=item["preview"])
''')
PAIRS.append(Pair(
    "author-rebuttal",
    "Preview computes the normalized payload without creating a delivery. Direct and deferred "
    "submissions are supported. drain delivers queued ordinary submissions once in order.",
    {"gateway.py": gateway, "service.py": service.split("    def drain")[0].replace(
        '        if defer:\n            self.pending.append({"payload": normalized, "preview": preview})\n            return normalized\n', "")},
    {"gateway.py": gateway, "service.py": service},
    ("service.py", 'self.gateway.send(item["payload"], preview=item["preview"])', 'self.gateway.send(item["payload"])'),
    source('''
        from gateway import Gateway
        from service import Service
        gateway = Gateway()
        service = Service(gateway)
        service.submit(" direct ", preview=True)
        service.submit(" queued ", preview=True, defer=True)
        service.submit(" ordinary ", defer=True)
        service.drain()
        return {"passes": gateway.deliveries == ["ordinary"], "observed": gateway.deliveries}
    '''),
    "The author's two source-backed statements do not establish that drain forwards the retained option. The adequate counterpart does forward it and defeats the concern.",
    "Thread t1, reviewer: Does the queued path preserve preview behavior?\n"
    "Thread t1, author: Gateway.send returns the normalized payload without creating a delivery "
    "when preview=True. The request options are retained with each queued record.\n",
))

envelope = source('''
    import json
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Completed:
        value: object

    class Envelope:
        def __init__(self, wire):
            self._raw = json.loads(wire)
            if not isinstance(self._raw, dict) or not isinstance(self._raw.get("state"), str):
                raise ValueError("invalid envelope")

        def to_wire(self):
            return json.dumps(self._raw)

        def completed(self):
            if self._raw["state"] != "done" or "value" not in self._raw:
                raise ValueError("not completed")
            return Completed(self._raw["value"])
''')
PAIRS.append(Pair(
    "valid-compatibility",
    "Envelope transports JSON objects with a string state. Vendor states and additional fields must "
    "round-trip unchanged as JSON values. The new completed() operation returns a Completed value only "
    "for state done with a value field; other envelopes remain transportable and cannot be consumed as Completed.",
    {"envelope.py": envelope.split("    def completed")[0]},
    {"envelope.py": envelope},
    ("envelope.py", '            raise ValueError("invalid envelope")',
     '            raise ValueError("invalid envelope")\n        if self._raw["state"] not in {"queued", "done", "error"}:\n            raise ValueError("unknown state")'),
    source('''
        import json
        from envelope import Envelope
        wire = {"state": "vendor:progress", "value": 3, "extension": {"x": True}}
        try:
            item = Envelope(json.dumps(wire))
            observed = json.loads(item.to_wire())
            try:
                item.completed()
                confined = False
            except ValueError:
                confined = True
        except ValueError:
            observed, confined = "rejected", False
        value = Envelope('{"state":"done","value":0}').completed().value
        return {"passes": observed == wire and confined and value == 0, "observed": observed}
    '''),
    "Closing the transport vocabulary rejects required valid vendor envelopes. The adequate boundary confines raw compatibility data and admits completed values on demand.",
))

ARMS = ("current-full", "compact-full", "current-facts")
ID = re.compile(r"[0-9a-f]{24}\Z")


def digest(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        name, data = path.relative_to(root).as_posix().encode(), path.read_bytes()
        h.update(len(name).to_bytes(8, "big") + name + len(data).to_bytes(8, "big") + data)
    return h.hexdigest()


def separate(path: Path, subjects: Path) -> None:
    if path == subjects or subjects in path.parents:
        raise ValueError("evaluator artifacts must be outside the reviewer export")


def write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        path.chmod(0o600)
        json.dump(value, stream, indent=2)
        stream.write("\n")


def export(subjects: Path, key_path: Path, seed: int | None = None) -> dict:
    subjects, key_path = subjects.resolve(), key_path.resolve()
    separate(key_path, subjects)
    if subjects.exists() or key_path.exists():
        raise ValueError("export and key destinations must be new")
    rng = random.Random(seed) if seed is not None else secrets.SystemRandom()
    cases = [(pair, variant) for pair in PAIRS for variant in ("adequate", "defective")]
    rng.shuffle(cases)
    subjects.mkdir(parents=True, mode=0o700)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key = {"schema": "elenctic-evaluation-key/v1", "subjects": {}}
    for pair, variant in cases:
        identity = f"{rng.getrandbits(96):024x}"
        while identity in key["subjects"]:
            identity = f"{rng.getrandbits(96):024x}"
        root = subjects / identity
        for side, files in (("base", pair.base), ("candidate", pair.files(variant))):
            (root / side).mkdir(parents=True)
            for name, contents in files.items():
                (root / side / name).write_text(contents, encoding="utf-8")
        (root / "SUBJECT.md").write_text(
            "# Review subject\n\nCompare base/ with candidate/. These are the complete relevant fixture sources. "
            "Read the supplied requirements and any discussion, discover supported findings, and state material "
            "limitations. Do not edit these files. This is an offline semantic review, not a native PR campaign.\n\n"
            "## Requirements\n\n" + pair.requirements + "\n", encoding="utf-8")
        if pair.discussion:
            (root / "DISCUSSION.md").write_text(pair.discussion, encoding="utf-8")
        key["subjects"][identity] = {
            "family": pair.name, "variant": variant,
            "expected": "BLOCKED" if variant == "defective" else "APPROVE",
            "basis": pair.basis, "digest": digest(root),
        }
    write_json(subjects / "manifest.json", {"schema": "elenctic-subjects/v1",
               "subjects": {identity: entry["digest"] for identity, entry in key["subjects"].items()}})
    write_json(key_path, key)
    return key


def check(subjects: Path, key_path: Path) -> list[dict]:
    subjects, key_path = subjects.resolve(), key_path.resolve()
    separate(key_path, subjects)
    key = json.loads(key_path.read_text(encoding="utf-8"))
    pairs = {pair.name: pair for pair in PAIRS}
    results = []
    for identity, entry in key["subjects"].items():
        if not ID.fullmatch(identity) or digest(subjects / identity) != entry["digest"]:
            raise ValueError("subject identity or source bytes changed")
        # Execute only this utility's probes on digest-matched synthetic sources.
        # -B prevents probes from changing the reviewed snapshots with bytecode.
        program = "import sys, os, json\nsys.path.insert(0, os.getcwd())\ndef probe():\n"
        program += textwrap.indent(pairs[entry["family"]].probe, "    ")
        program += "\nprint(json.dumps(probe()))\n"
        completed = subprocess.run([sys.executable, "-I", "-B", "-c", program],
                                   cwd=subjects / identity / "candidate", capture_output=True, text=True, timeout=5)
        if completed.returncode:
            raise ValueError(f"fixture probe failed for {identity}: {completed.stderr}")
        result = json.loads(completed.stdout)
        if result["passes"] is not (entry["variant"] == "adequate"):
            raise ValueError(f"fixture contradicts evaluator key: {identity}")
        results.append({"subject": identity, **result})
    return results


def record(subjects: Path, identity: str, arm: str, report: Path, records: Path,
           execution: str = "isolated-semantic", context: Path | None = None) -> dict:
    subjects, records = subjects.resolve(), records.resolve()
    separate(records, subjects)
    manifest = json.loads((subjects / "manifest.json").read_text(encoding="utf-8"))
    if (not ID.fullmatch(identity) or identity not in manifest["subjects"] or arm not in ARMS
            or execution not in ("isolated-semantic", "seeded-comparison", "native-campaign")):
        raise ValueError("unknown subject or arm")
    root = subjects / identity
    if not root.is_dir() or digest(root) != manifest["subjects"][identity]:
        raise ValueError("reviewed subject is missing or changed")
    payload = report.read_bytes()
    context_bytes = context.read_bytes() if context else None
    records.mkdir(parents=True, exist_ok=True, mode=0o700)
    run = secrets.token_hex(12)
    raw_path = records / (run + ".report")
    with raw_path.open("xb") as stream:
        raw_path.chmod(0o600)
        stream.write(payload)
    context_path = records / (run + ".context") if context_bytes is not None else None
    if context_path:
        with context_path.open("xb") as stream:
            context_path.chmod(0o600)
            stream.write(context_bytes)
    receipt = {"schema": "elenctic-evaluation-report/v1", "run": run, "subject": identity,
               "arm": arm, "execution": execution, "source_digest": manifest["subjects"][identity],
               "report": raw_path.name, "report_sha256": hashlib.sha256(payload).hexdigest(),
               "context": context_path.name if context_path else None,
               "context_sha256": hashlib.sha256(context_bytes).hexdigest() if context_bytes is not None else None}
    write_json(records / (run + ".json"), receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("export")
    create.add_argument("--subjects", type=Path, required=True)
    create.add_argument("--key", type=Path, required=True)
    create.add_argument("--seed", type=int)
    probe = commands.add_parser("check")
    probe.add_argument("--subjects", type=Path, required=True)
    probe.add_argument("--key", type=Path, required=True)
    capture = commands.add_parser("record")
    capture.add_argument("--subjects", type=Path, required=True)
    capture.add_argument("--subject", required=True)
    capture.add_argument("--arm", choices=ARMS, required=True)
    capture.add_argument("--report", type=Path, required=True)
    capture.add_argument("--records", type=Path, required=True)
    capture.add_argument("--execution", choices=("isolated-semantic", "seeded-comparison", "native-campaign"),
                         default="isolated-semantic")
    capture.add_argument("--context", type=Path, help="exact supplied prompt/context and declared runtime settings")
    args = parser.parse_args()
    try:
        if args.command == "export":
            key = export(args.subjects, args.key, args.seed)
            print(json.dumps({"subjects": len(key["subjects"]), "model_evaluation": "unrun"}))
        elif args.command == "check":
            print(json.dumps({"probes": check(args.subjects, args.key), "model_evaluation": "unrun"}, indent=2))
        else:
            print(json.dumps(record(args.subjects, args.subject, args.arm, args.report, args.records,
                                    args.execution, args.context), indent=2))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(2, f"{error}\n")


if __name__ == "__main__":
    main()

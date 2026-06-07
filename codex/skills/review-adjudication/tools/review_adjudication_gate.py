#!/usr/bin/env python3
"""Mechanical gate checker for Kernelized Surface-Budgeted v9 review-adjudication outputs.

The checker validates the always-on Claim Decision Kernel, Resolution Warrants,
route-triggered annexes, surface budgets, handoff agenda consistency, and optional
diffstat/changed-file budget consumption. It cannot prove semantic correctness;
it blocks unlicensed or inconsistent downstream action.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ROUTES = {
    "address",
    "validate-only",
    "resolve-thread-only",
    "do-not-address",
    "delete-collapse-canonicalize",
    "blocked",
}
STATUSES = {
    "licensed",
    "validation-needed",
    "proof-only",
    "no-change",
    "delete-collapse-canonicalize",
    "blocked",
}
ACTIONS = {"mutate-code", "add-validation-only", "resolve-thread", "draft-reply", "defer", "none"}
ACTION_BY_ROUTE = {
    "address": {"mutate-code"},
    "delete-collapse-canonicalize": {"mutate-code"},
    "validate-only": {"add-validation-only"},
    "resolve-thread-only": {"resolve-thread"},
    "do-not-address": {"draft-reply", "defer", "none"},
    "blocked": {"none"},
}
SURFACE_MODES = {"ablative-first", "additive-authorized", "proof-only", "validation-only", "not-applicable"}
TARGET_NET_LOC = {"negative", "zero", "small-positive", "unknown", "not-applicable"}
EXPANSION_STATUS = {"not-needed", "needed", "granted", "blocked", "not-applicable"}
GATE_FIELDS = [
    "claimkernelcomplete",
    "artifactstatebound",
    "warrantcoverage",
    "routeannexescomplete",
    "surfacebudgetcoverage",
    "fixedpointhandoffcomplete",
    "handoffagendaconsistency",
    "adjudicationcomplete",
    "implementationhandoffallowed",
    "validationhandoffallowed",
    "replyhandoffallowed",
]
REQUIRED_ALWAYS = [
    "Review Basis",
    "Claim Decision Kernel",
    "Resolution Warrants",
    "Adjudication Gate",
    "Handoff Agenda",
    "Adjudication Bottom Line",
]
REQUIRED_MUTATION = [
    "Resolve Countercases",
    "Adversarial Action Matrix",
    "Ablative Counterproposal Ledger",
    "Surface Budget Ledger",
    "Warrant / Budget Summary",
]
REQUIRED_DELETE = ["Ablative Isomorphism Cards"]
OPTIONAL_SINGLETONS = {
    "Resolve Countercases",
    "Adversarial Action Matrix",
    "Ablative Counterproposal Ledger",
    "Ablative Isomorphism Cards",
    "Surface Budget Ledger",
    "Warrant / Budget Summary",
}
EMPTY = {"", "-", "—", "n/a", "na", "none", "[]"}
GENERIC_PROOF = {"code", "tests", "review", "proof", "current-artifacts", "looks-right", "reviewer-said-so"}

KERNEL_ALIASES = {
    "idthread": "id",
    "id": "id",
    "commentid": "id",
    "threadid": "id",
    "findingid": "id",
    "claim": "claim",
    "currentstatetruth": "truth",
    "truth": "truth",
    "route": "route",
    "resolvedecision": "route",
    "warrantid": "warrantid",
    "warrant": "warrantid",
    "proofref": "proofref",
    "proof": "proofref",
    "evidenceref": "proofref",
    "status": "status",
}
WARRANT_ALIASES = {
    "warrantid": "warrantid",
    "warrant": "warrantid",
    "claimid": "claimid",
    "idthread": "claimid",
    "commentid": "claimid",
    "threadid": "claimid",
    "source": "source",
    "selectedroute": "route",
    "route": "route",
    "resolvedecision": "route",
    "permittedaction": "action",
    "action": "action",
    "permittedscope": "scope",
    "scope": "scope",
    "forbiddenactions": "forbidden",
    "forbidden": "forbidden",
    "evidencerefs": "evidence",
    "evidenceref": "evidence",
    "evidence": "evidence",
    "countercaseref": "countercase",
    "countercase": "countercase",
    "proofrequired": "proofrequired",
    "proof": "proofrequired",
    "expiry": "expiry",
    "expires": "expiry",
}
BUDGET_ALIASES = {
    "warrantid": "warrantid",
    "mode": "mode",
    "targetnetloc": "targetnetloc",
    "maxpositiveloc": "maxpositiveloc",
    "maxnewpublicsymbols": "maxnewpublicsymbols",
    "maxnewfiles": "maxnewfiles",
    "maxnewhelpers": "maxnewhelpers",
    "maxnewflagsknobs": "maxnewflagsknobs",
    "maxnewflagsorknobs": "maxnewflagsknobs",
    "maxnewstatevariants": "maxnewstatevariants",
    "maxnewbranches": "maxnewbranches",
    "duplicatepathbudget": "duplicatepathbudget",
    "subtractiveprobesrequired": "subtractiveprobesrequired",
    "expansionwarrantrequired": "expansionwarrantrequired",
    "expansionstatus": "expansionstatus",
    "proofrequired": "proofrequired",
    "notes": "notes",
}
GATE_ALIASES = {
    "claimkernelcomplete": "claimkernelcomplete",
    "kernelcomplete": "claimkernelcomplete",
    "artifactstatebound": "artifactstatebound",
    "warrantcoverage": "warrantcoverage",
    "routeannexescomplete": "routeannexescomplete",
    "surfacebudgetcoverage": "surfacebudgetcoverage",
    "fixedpointhandoffcomplete": "fixedpointhandoffcomplete",
    "handoffagendaconsistency": "handoffagendaconsistency",
    "adjudicationcomplete": "adjudicationcomplete",
    "implementationhandoffallowed": "implementationhandoffallowed",
    "validationhandoffallowed": "validationhandoffallowed",
    "replyhandoffallowed": "replyhandoffallowed",
}
HANDOFF_ALIASES = {
    "implementationitems": "implementation",
    "deletecollapsecanonicalizeitems": "delete",
    "deletecollapseitems": "delete",
    "validationonlyitems": "validation",
    "proofonlythreadresolutionitems": "proofonly",
    "replydefernochangeitems": "reply",
    "blockeditems": "blocked",
    "fixedpointdriversurfacehandshakerequired": "fixedpoint",
}

@dataclass
class CheckResult:
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)
    gate: Dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({"passed": self.passed, "errors": self.errors, "warnings": self.warnings, "stats": self.stats, "gate": self.gate}, indent=2, sort_keys=True)


def norm_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.strip().lower())


def norm_value(value: str) -> str:
    value = re.sub(r"[`*_]", "", value.strip().lower())
    return re.sub(r"\s+", "-", value)


def is_empty(value: str) -> bool:
    return norm_value(value) in EMPTY or norm_value(value) == "unknown"


def section_count(text: str, title: str) -> int:
    return len(re.findall(rf"(?im)^\s*#+\s+{re.escape(title)}\s*$", text))


def has_section(text: str, title: str) -> bool:
    return section_count(text, title) > 0


def section_text(text: str, title: str) -> str:
    match = re.search(rf"(?im)^\s*#+\s+{re.escape(title)}\s*$", text)
    if not match:
        return ""
    start = match.end()
    nxt = re.search(r"(?m)^\s*#+\s+", text[start:])
    end = start + nxt.start() if nxt else len(text)
    return text[start:end].strip()


def split_row(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def is_sep(cells: Sequence[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c.strip()) for c in cells)


def table(block: str) -> Tuple[List[str], List[Dict[str, str]]]:
    lines = [line.rstrip() for line in block.splitlines()]
    rows: List[str] = []
    started = False
    for line in lines:
        if line.strip().startswith("|"):
            rows.append(line)
            started = True
        elif started and not line.strip():
            break
        elif started:
            break
    if len(rows) < 2:
        return [], []
    headers = split_row(rows[0])
    if not is_sep(split_row(rows[1])):
        return [], []
    data = []
    for line in rows[2:]:
        cells = split_row(line)
        if len(cells) < len(headers):
            cells += [""] * (len(headers) - len(cells))
        data.append({headers[i]: cells[i] for i in range(len(headers))})
    return headers, data


def normalize(headers: Sequence[str], rows: Sequence[Dict[str, str]], aliases: Dict[str, str]) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    hmap: Dict[str, str] = {}
    for h in headers:
        canonical = aliases.get(norm_key(h))
        if canonical:
            hmap[canonical] = h
    out = []
    for row in rows:
        item = {}
        for canonical, original in hmap.items():
            item[canonical] = row.get(original, "").strip()
        out.append(item)
    return hmap, out


def rows_by_id(rows: Sequence[Dict[str, str]], key: str = "id") -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for row in rows:
        rid = row.get(key, "").strip()
        if rid:
            out[rid] = row
    return out


def proof_is_concrete(value: str, allow_missing: bool = False) -> bool:
    if allow_missing and norm_value(value) in {"missing", "blocked", "unknown"}:
        return True
    if is_empty(value):
        return False
    nv = norm_value(value)
    if nv in GENERIC_PROOF:
        return False
    if re.search(r"[\w./-]+:\d+", value):
        return True
    if any(tok in nv for tok in ["test", "ci", "cmd", "command", "log", "thread", "pr#", "github", "commit", "diff", "src/", "tests/"]):
        return True
    return "/" in value or "." in value or "#" in value or len(value.strip()) >= 16


def parse_id_list(value: str) -> List[str]:
    if is_empty(value):
        return []
    return [p.strip().strip('`"\'') for p in re.split(r"[,;\s]+", value) if p.strip().strip('`"\'')]


def parse_handoff(block: str, known_ids: Iterable[str], errors: List[str]) -> Dict[str, List[str]]:
    fields: Dict[str, str] = {}
    for line in block.splitlines():
        stripped = re.sub(r"^[-*]\s+", "", line.strip())
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        canonical = HANDOFF_ALIASES.get(norm_key(key))
        if canonical:
            fields[canonical] = value.strip()
    buckets = {"implementation": [], "delete": [], "validation": [], "proofonly": [], "reply": [], "blocked": []}
    for name in buckets:
        raw = fields.get(name, "")
        if not raw:
            errors.append(f"Handoff Agenda missing `{name}` bucket")
            continue
        if re.search(r"(?i)\ball\b", raw):
            errors.append(f"Handoff Agenda `{name}` uses broad `all`; explicit ids are required")
            continue
        if is_empty(raw):
            continue
        found = [rid for rid in known_ids if re.search(rf"(?<![A-Za-z0-9_.:-]){re.escape(rid)}(?![A-Za-z0-9_.:-])", raw)]
        buckets[name] = found if found else parse_id_list(raw)
    buckets["fixedpoint"] = [norm_value(fields.get("fixedpoint", ""))]
    return buckets


def parse_gate(text: str) -> Dict[str, str]:
    headers, raw = table(section_text(text, "Adjudication Gate"))
    if not headers:
        return {}
    field_h = value_h = None
    for h in headers:
        nk = norm_key(h)
        if nk in {"field", "check", "gatefield"}:
            field_h = h
        if nk in {"value", "status", "result"}:
            value_h = h
    if not field_h or not value_h:
        if len(headers) >= 2:
            field_h, value_h = headers[0], headers[1]
        else:
            return {}
    gate = {}
    for row in raw:
        key = GATE_ALIASES.get(norm_key(row.get(field_h, "")))
        if key:
            gate[key] = norm_value(row.get(value_h, ""))
    return gate


def int_or_none(value: str) -> Optional[int]:
    m = re.search(r"-?\d+", value or "")
    return int(m.group(0)) if m else None


def parse_diffstat(diffstat: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    ins_m = re.search(r"(\d+)\s+insertions?\(\+\)", diffstat)
    del_m = re.search(r"(\d+)\s+deletions?\(-\)", diffstat)
    ins = int(ins_m.group(1)) if ins_m else None
    dels = int(del_m.group(1)) if del_m else None
    net = (ins or 0) - (dels or 0) if ins is not None or dels is not None else None
    return ins, dels, net


def check(text: str, *, changed_files: Optional[Sequence[str]] = None, diffstat: Optional[str] = None, resolved_threads: Optional[Sequence[str]] = None) -> CheckResult:
    errors: List[str] = []
    warnings: List[str] = []

    for sec in REQUIRED_ALWAYS:
        count = section_count(text, sec)
        if count != 1:
            errors.append(f"{sec} must appear exactly once, found {count}")
    for sec in OPTIONAL_SINGLETONS:
        count = section_count(text, sec)
        if count > 1:
            errors.append(f"{sec} must appear at most once, found {count}")

    basis = section_text(text, "Review Basis")
    if "artifact_state_id" not in basis:
        errors.append("Review Basis missing artifact_state_id")
    for k in ["branch", "head", "diff_digest"]:
        if basis and not re.search(rf"(?im)^\s*{re.escape(k)}\s*:", basis):
            errors.append(f"artifact_state_id missing `{k}`")

    kh, kr = table(section_text(text, "Claim Decision Kernel"))
    kmap, kernel_rows = normalize(kh, kr, KERNEL_ALIASES)
    missing = [f for f in ["id", "claim", "truth", "route", "warrantid", "proofref", "status"] if f not in kmap]
    if missing:
        errors.append("Claim Decision Kernel missing required columns: " + ", ".join(missing))
    if not kernel_rows:
        errors.append("Claim Decision Kernel has no rows")
    kernel_by_id = rows_by_id(kernel_rows)
    if len(kernel_by_id) != len(kernel_rows):
        errors.append("Claim Decision Kernel has duplicate or empty ids")

    mutation_ids: List[str] = []
    delete_ids: List[str] = []
    validation_ids: List[str] = []
    proof_ids: List[str] = []
    reply_ids: List[str] = []
    blocked_ids: List[str] = []
    for row in kernel_rows:
        rid = row.get("id", "")
        route = norm_value(row.get("route", ""))
        status = norm_value(row.get("status", ""))
        proof = row.get("proofref", "")
        if route not in ROUTES:
            errors.append(f"{rid}: invalid route `{row.get('route', '')}`")
        if status not in STATUSES:
            errors.append(f"{rid}: invalid status `{row.get('status', '')}`")
        if not proof_is_concrete(proof, allow_missing=(route == "blocked")):
            errors.append(f"{rid}: kernel proof ref is not concrete")
        if route == "address":
            mutation_ids.append(rid)
        elif route == "delete-collapse-canonicalize":
            mutation_ids.append(rid); delete_ids.append(rid)
        elif route == "validate-only":
            validation_ids.append(rid)
        elif route == "resolve-thread-only":
            proof_ids.append(rid)
        elif route == "do-not-address":
            reply_ids.append(rid)
        elif route == "blocked":
            blocked_ids.append(rid)

    wh, wr = table(section_text(text, "Resolution Warrants"))
    wmap, warrants = normalize(wh, wr, WARRANT_ALIASES)
    missing = [f for f in ["warrantid", "claimid", "source", "route", "action", "scope", "forbidden", "evidence", "countercase", "proofrequired", "expiry"] if f not in wmap]
    if missing:
        errors.append("Resolution Warrants missing required columns: " + ", ".join(missing))
    warrant_by_claim: Dict[str, Dict[str, str]] = {}
    for row in warrants:
        wid = row.get("warrantid", "")
        cid = row.get("claimid", "")
        route = norm_value(row.get("route", ""))
        action = norm_value(row.get("action", ""))
        if not wid or not cid:
            errors.append("Resolution Warrants row missing warrant id or claim id")
            continue
        if cid in warrant_by_claim:
            errors.append(f"{cid}: duplicate warrant claim id")
        warrant_by_claim[cid] = row
        kernel = kernel_by_id.get(cid)
        if not kernel:
            errors.append(f"{wid}: warrant claim `{cid}` not found in kernel")
            continue
        if wid != kernel.get("warrantid"):
            errors.append(f"{cid}: warrant id `{wid}` does not match kernel `{kernel.get('warrantid')}`")
        if route != norm_value(kernel.get("route", "")):
            errors.append(f"{cid}: warrant route `{route}` does not match kernel route `{norm_value(kernel.get('route', ''))}`")
        if action not in ACTIONS:
            errors.append(f"{wid}: invalid permitted action `{row.get('action', '')}`")
        elif action not in ACTION_BY_ROUTE.get(route, set()):
            errors.append(f"{wid}: route `{route}` cannot issue permitted action `{action}`")
        if action == "mutate-code":
            if is_empty(row.get("scope", "")) or norm_value(row.get("scope", "")) in {"all", "repo", "whole-repo", "everything"}:
                errors.append(f"{wid}: mutate-code requires narrow permitted scope")
            forbidden = norm_value(row.get("forbidden", ""))
            if "outside" not in forbidden and "mutate" not in forbidden:
                errors.append(f"{wid}: mutate-code warrant must forbid out-of-scope mutation")
            if not proof_is_concrete(row.get("evidence", "")):
                errors.append(f"{wid}: mutate-code warrant needs concrete evidence refs")
        if action == "add-validation-only" and "production" not in norm_value(row.get("forbidden", "")):
            errors.append(f"{wid}: validation-only warrant must forbid production mutation")
        if action != "none" and is_empty(row.get("proofrequired", "")):
            errors.append(f"{wid}: non-none warrant requires proof_required")
        if is_empty(row.get("countercase", "")):
            errors.append(f"{wid}: missing countercase ref")
        expiry = norm_value(row.get("expiry", ""))
        if not any(tok in expiry for tok in ["head", "base", "artifact", "diff", "claim", "comment", "thread"]):
            errors.append(f"{wid}: expiry must mention artifact/comment invalidation")
    if set(kernel_by_id) != set(warrant_by_claim):
        missing_warrants = sorted(set(kernel_by_id) - set(warrant_by_claim))
        extra_warrants = sorted(set(warrant_by_claim) - set(kernel_by_id))
        if missing_warrants:
            errors.append("Resolution Warrants missing claims: " + ", ".join(missing_warrants))
        if extra_warrants:
            errors.append("Resolution Warrants contain unknown claims: " + ", ".join(extra_warrants))

    if mutation_ids:
        for sec in REQUIRED_MUTATION:
            if section_count(text, sec) != 1:
                errors.append(f"mutation-capable routes require {sec}")
    if delete_ids:
        for sec in REQUIRED_DELETE:
            if section_count(text, sec) != 1:
                errors.append(f"delete-collapse-canonicalize routes require {sec}")

    budget_by_warrant: Dict[str, Dict[str, str]] = {}
    if mutation_ids and has_section(text, "Surface Budget Ledger"):
        bh, br = table(section_text(text, "Surface Budget Ledger"))
        bmap, budgets = normalize(bh, br, BUDGET_ALIASES)
        missing = [f for f in ["warrantid", "mode", "targetnetloc", "maxpositiveloc", "maxnewpublicsymbols", "maxnewfiles", "maxnewhelpers", "maxnewflagsknobs", "maxnewstatevariants", "maxnewbranches", "duplicatepathbudget", "subtractiveprobesrequired", "expansionwarrantrequired", "expansionstatus", "proofrequired", "notes"] if f not in bmap]
        if missing:
            errors.append("Surface Budget Ledger missing required columns: " + ", ".join(missing))
        for row in budgets:
            wid = row.get("warrantid", "")
            budget_by_warrant[wid] = row
            mode = norm_value(row.get("mode", ""))
            target = norm_value(row.get("targetnetloc", ""))
            expansion = norm_value(row.get("expansionstatus", ""))
            if mode not in SURFACE_MODES:
                errors.append(f"{wid}: invalid surface budget mode `{row.get('mode', '')}`")
            if target not in TARGET_NET_LOC:
                errors.append(f"{wid}: invalid target net loc `{row.get('targetnetloc', '')}`")
            if expansion not in EXPANSION_STATUS:
                errors.append(f"{wid}: invalid expansion status `{row.get('expansionstatus', '')}`")
            if norm_value(row.get("subtractiveprobesrequired", "")) not in {"yes", "no"}:
                errors.append(f"{wid}: subtractive probes required must be yes/no")
            if mode == "additive-authorized" and norm_value(row.get("expansionstatus", "")) not in {"granted", "not-needed"}:
                errors.append(f"{wid}: additive-authorized requires expansion status granted or not-needed")
            if is_empty(row.get("proofrequired", "")):
                errors.append(f"{wid}: surface budget requires proof required")
        for cid in mutation_ids:
            warrant = warrant_by_claim.get(cid)
            if warrant and warrant.get("warrantid") not in budget_by_warrant:
                errors.append(f"{cid}: mutate-code warrant lacks Surface Budget Ledger row")

    handoff = parse_handoff(section_text(text, "Handoff Agenda"), list(kernel_by_id), errors)
    expected_impl = sorted([cid for cid in mutation_ids if cid not in delete_ids])
    if sorted(handoff.get("implementation", [])) != expected_impl:
        errors.append(f"Handoff implementation items {sorted(handoff.get('implementation', []))} do not match address routes {expected_impl}")
    if sorted(handoff.get("delete", [])) != sorted(delete_ids):
        errors.append(f"Handoff delete/collapse items {sorted(handoff.get('delete', []))} do not match delete-collapse-canonicalize routes {sorted(delete_ids)}")
    if sorted(handoff.get("validation", [])) != sorted(validation_ids):
        errors.append(f"Handoff validation items {sorted(handoff.get('validation', []))} do not match validate-only routes {sorted(validation_ids)}")
    if sorted(handoff.get("proofonly", [])) != sorted(proof_ids):
        errors.append(f"Handoff proof-only items {sorted(handoff.get('proofonly', []))} do not match resolve-thread-only routes {sorted(proof_ids)}")
    if sorted(handoff.get("blocked", [])) != sorted(blocked_ids):
        errors.append(f"Handoff blocked items {sorted(handoff.get('blocked', []))} do not match blocked routes {sorted(blocked_ids)}")
    if mutation_ids and handoff.get("fixedpoint", [""])[0] != "yes":
        errors.append("mutation-capable routes require fixed-point-driver surface handshake required: yes")

    if changed_files:
        for f in changed_files:
            matched = False
            for cid in mutation_ids:
                w = warrant_by_claim.get(cid, {})
                scope = w.get("scope", "")
                if f and (f in scope or any(part and part in scope for part in f.split("/")[-1:])):
                    matched = True
                    break
            if not matched:
                errors.append(f"changed file `{f}` is not covered by any mutate-code permitted scope")
    if resolved_threads:
        for t in resolved_threads:
            if t not in proof_ids and t not in mutation_ids:
                warnings.append(f"resolved thread `{t}` was not matched to a resolve-thread-only/address claim id")
    if diffstat and mutation_ids:
        ins, dels, net = parse_diffstat(diffstat)
        if net is not None:
            for cid in mutation_ids:
                w = warrant_by_claim.get(cid, {})
                b = budget_by_warrant.get(w.get("warrantid", ""), {})
                target = norm_value(b.get("targetnetloc", ""))
                max_pos = int_or_none(b.get("maxpositiveloc", ""))
                expansion = norm_value(b.get("expansionstatus", ""))
                if target == "negative" and net >= 0 and expansion != "granted":
                    errors.append(f"{cid}: target net loc negative but diffstat net is {net} without granted expansion")
                if target == "zero" and net > 0 and expansion != "granted":
                    errors.append(f"{cid}: target net loc zero but diffstat net is {net} without granted expansion")
                if max_pos is not None and ins is not None and len(mutation_ids) == 1 and ins > max_pos and expansion != "granted":
                    errors.append(f"{cid}: insertions {ins} exceed max positive loc {max_pos} without granted expansion")
                elif max_pos is not None and ins is not None and len(mutation_ids) > 1 and ins > max_pos and expansion != "granted":
                    warnings.append(f"{cid}: aggregate insertions {ins} exceed per-warrant max positive loc {max_pos}; run a per-warrant diffstat for strict budget enforcement")

    gate = parse_gate(text)
    for f in GATE_FIELDS:
        if f not in gate:
            errors.append(f"Adjudication Gate missing `{f}`")
    for f, value in gate.items():
        if f.endswith("allowed"):
            if value not in {"yes", "no"}:
                errors.append(f"{f} must be yes/no")
        else:
            if value not in {"pass", "fail", "not-required", "not-applicable"}:
                errors.append(f"{f} must be pass/fail/not-required/not-applicable")
    failing_gate = [f for f, v in gate.items() if v == "fail"]
    if failing_gate and gate.get("adjudicationcomplete") == "pass":
        errors.append("adjudication_complete is pass despite failed gate fields: " + ", ".join(sorted(failing_gate)))
    if errors and gate.get("adjudicationcomplete") == "pass":
        errors.append("adjudication_complete is pass despite mechanical errors")
    if errors and gate.get("implementationhandoffallowed") == "yes":
        errors.append("implementation_handoff_allowed is yes despite mechanical errors")
    if gate.get("implementationhandoffallowed") == "yes" and not mutation_ids:
        errors.append("implementation_handoff_allowed is yes but no mutation-capable routes exist")
    if (errors or failing_gate) and "blocked" not in section_text(text, "Adjudication Bottom Line").lower():
        errors.append("failed gate or mechanical error requires blocked Adjudication Bottom Line")

    stats = {
        "claims": len(kernel_rows),
        "address": len([r for r in kernel_rows if norm_value(r.get("route", "")) == "address"]),
        "delete_collapse_canonicalize": len(delete_ids),
        "validate_only": len(validation_ids),
        "resolve_thread_only": len(proof_ids),
        "do_not_address": len(reply_ids),
        "blocked": len(blocked_ids),
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return CheckResult(not errors, errors, warnings, stats, gate)


def print_human(result: CheckResult) -> None:
    print("PASS: Kernelized Surface-Budgeted v9 gate satisfied" if result.passed else "FAIL: Kernelized Surface-Budgeted v9 gate incomplete")
    print("stats:", ", ".join(f"{k}={v}" for k, v in result.stats.items()))
    if result.gate:
        print("gate:", ", ".join(f"{k}={v}" for k, v in result.gate.items()))
    if result.errors:
        print("errors:")
        for e in result.errors:
            print(f"- {e}")
    if result.warnings:
        print("warnings:")
        for w in result.warnings:
            print(f"- {w}")


def valid_fixture() -> str:
    return """
## Review Basis

artifact_state_id:
  branch: feature/review
  base: main@abc123
  head: feature@def456
  diff_digest: paths=src/a.py,tests/test_a.py
  claim_set_digest: c1,c2,c3,c4
  ci_state: local tests pass

## Claim Decision Kernel

| id/thread | claim | current-state truth | route | warrant id | proof ref | status |
|---|---|---|---|---|---|---|
| c1 | retry duplicates writes | src/a.py currently lacks idempotence guard | address | rw-c1 | src/a.py:10 | licensed |
| c2 | flake may exist | not proven on current artifacts | validate-only | rw-c2 | thread:c2 | validation-needed |
| c3 | helper rename | no convention supports rename | do-not-address | rw-c3 | src/a.py:1 | no-change |
| c4 | duplicate wrapper path | same contract can be canonicalized | delete-collapse-canonicalize | rw-c4 | src/a.py:20 | delete-collapse-canonicalize |

## Resolution Warrants

| warrant id | claim id | source | selected route | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | c1 | github-review | address | mutate-code | src/a.py, tests/test_a.py | forbid mutate outside permitted scope | src/a.py:10 | no-change defeated at src/a.py:10 | pytest tests/test_a.py::test_retry_idempotent | expires when head/base/diff/comment changes |
| rw-c2 | c2 | github-review | validate-only | add-validation-only | tests/test_a.py | forbid production mutation | thread:c2 | flake unproven | add validation probe only | expires when head/base/diff/comment changes |
| rw-c3 | c3 | github-review | do-not-address | none | none | no mutation | src/a.py:1 | preference-only preserved | none | expires when head/base/diff/comment changes |
| rw-c4 | c4 | github-review | delete-collapse-canonicalize | mutate-code | src/a.py, tests/test_a.py | forbid mutate outside permitted scope | src/a.py:20 | duplicate wrapper dominated | pytest tests/test_a.py::test_retry_idempotent | expires when head/base/diff/comment changes |

## Resolve Countercases

| id/thread | selected route | strongest alternative route | countercase status | evidence ref | route impact |
|---|---|---|---|---|---|
| c1 | address | validate-only | defeated | src/a.py:10 | mutate allowed under budget |
| c2 | validate-only | address | preserved-validate-first | thread:c2 | validation only |
| c3 | do-not-address | address | preserved-no-change | src/a.py:1 | no implementation |
| c4 | delete-collapse-canonicalize | additive-helper | preserved-ablative | src/a.py:20 | canonicalize not add |

## Adversarial Action Matrix

| id/thread | selected route | adversarial challenge | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|
| c1 | address | validation-first could be enough | cleared | cleared | src/a.py:10 | address preserved |
| c4 | delete-collapse-canonicalize | deletion could lose behavior | cleared | cleared | tests/test_a.py::test_retry_idempotent | canonicalize preserved |

## Ablative Counterproposal Ledger

| id/thread | additive proposal | delete candidate | collapse/reuse candidate | canonical owner candidate | privatization/decommission candidate | clone classification | abstraction-ladder check | lower-surface route | why insufficient or selected | ablative clearance | proof ref |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | add guard | none | reuse retry state | retry state | none | not-applicable | not-needed | none | lower-surface not enough for missing guard | clear-additive | src/a.py:10 |
| c4 | add helper | wrapper path | canonical retry state | retry state | wrapper private | exact-clone | not-needed | canonicalize | canonical owner selected | select-ablative-route | src/a.py:20 |

## Ablative Isomorphism Cards

| id/thread | surface | proposed action | behavior preserved | public contract preserved | error/order/side effects preserved | compatibility risk | proof signal | card status |
|---|---|---|---|---|---|---|---|---|
| c4 | duplicate wrapper | canonicalize | yes | yes | yes | low | tests/test_a.py::test_retry_idempotent | pass |

## Surface Budget Ledger

| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | subtractive probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | ablative-first | small-positive | 20 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | yes | yes | not-needed | pytest tests/test_a.py::test_retry_idempotent | narrow guard only |
| rw-c4 | ablative-first | negative | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | yes | yes | not-needed | pytest tests/test_a.py::test_retry_idempotent | canonicalize wrapper |

## Act On

- c1: mutate within rw-c1 scope only.

## Validate Only

- c2: add validation probe only.

## Delete / Collapse / Canonicalize

- c4: canonicalize duplicate wrapper.

## Rebut / Do Not Address

- c3: no-change.

## Need Evidence / Blocked

- none.

## Warrant / Budget Summary

| warrant id | claim id | route | permitted action | surface budget status | ablation status | implementation allowed |
|---|---|---|---|---|---|---|
| rw-c1 | c1 | address | mutate-code | within-budget | clear-additive | yes |
| rw-c4 | c4 | delete-collapse-canonicalize | mutate-code | within-budget | select-ablative-route | yes |

## Adjudication Gate

| field | value | basis |
|---|---|---|
| claim_kernel_complete | pass | four raw claims represented |
| artifact_state_bound | pass | artifact_state_id recorded |
| warrant_coverage | pass | every kernel row has matching warrant |
| route_annexes_complete | pass | mutation/delete annexes present |
| surface_budget_coverage | pass | mutation warrants budgeted |
| fixed_point_handoff_complete | pass | handoff requests surface handshake |
| handoff_agenda_consistency | pass | agenda ids match routes |
| adjudication_complete | pass | all required fields pass |
| implementation_handoff_allowed | yes | c1 and c4 have mutate-code warrants |
| validation_handoff_allowed | yes | c2 has add-validation-only warrant |
| reply_handoff_allowed | yes | c3 has no-change/reply route |

## Handoff Agenda

- implementation items: c1
- delete/collapse/canonicalize items: c4
- validation-only items: c2
- proof-only thread-resolution items: none
- reply/defer/no-change items: c3
- blocked items: none
- fixed-point-driver surface handshake required: yes
- proof: pytest tests/test_a.py::test_retry_idempotent

## Adjudication Bottom Line

Proceed: c1 and c4 may route to fixed-point-driver under scoped surface budgets; c2 is validation-only; c3 is no-change.
"""


def invalid_fixture() -> str:
    return """
## Review Basis
artifact_state_id:
  branch: f
  head: h
  diff_digest: d

## Claim Decision Kernel
| id/thread | claim | current-state truth | route | warrant id | proof ref | status |
|---|---|---|---|---|---|---|
| c1 | add helper | plausible | address | rw-c1 | code | licensed |

## Resolution Warrants
| warrant id | claim id | source | selected route | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | c1 | review | address | mutate-code | all | none | code | none | test | never |

## Adjudication Gate
| field | value | basis |
|---|---|---|
| claim_kernel_complete | pass | bad |
| artifact_state_bound | pass | bad |
| warrant_coverage | pass | bad |
| route_annexes_complete | pass | bad |
| surface_budget_coverage | pass | bad |
| fixed_point_handoff_complete | pass | bad |
| handoff_agenda_consistency | pass | bad |
| adjudication_complete | pass | bad |
| implementation_handoff_allowed | yes | bad |
| validation_handoff_allowed | no | bad |
| reply_handoff_allowed | no | bad |

## Handoff Agenda
- implementation items: all
- delete/collapse/canonicalize items: none
- validation-only items: none
- proof-only thread-resolution items: none
- reply/defer/no-change items: none
- blocked items: none
- fixed-point-driver surface handshake required: no
- proof: test

## Adjudication Bottom Line
Proceed.
"""


def run_self_test() -> int:
    good = check(valid_fixture())
    bad = check(invalid_fixture())
    if good.passed and not bad.passed:
        print("self-test passed")
        return 0
    print("self-test failed")
    print("valid:", good.to_json())
    print("invalid:", bad.to_json())
    return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="Markdown adjudication output")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--changed-files", default="", help="comma-separated changed files for warrant scope check")
    parser.add_argument("--resolved-threads", default="", help="comma-separated resolved thread/claim ids")
    parser.add_argument("--diffstat", default="", help="git diff --stat summary string")
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()
    if not args.path:
        parser.error("path is required unless --self-test is used")
    text = Path(args.path).read_text(encoding="utf-8")
    changed = [x.strip() for x in args.changed_files.split(",") if x.strip()] or None
    resolved = [x.strip() for x in args.resolved_threads.split(",") if x.strip()] or None
    result = check(text, changed_files=changed, resolved_threads=resolved, diffstat=args.diffstat or None)
    if args.json:
        print(result.to_json())
    else:
        print_human(result)
    return 0 if result.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

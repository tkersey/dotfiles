#!/usr/bin/env python3
"""Mechanical contract checker for Authority-Gated v1 adversarial-reviewer outputs.

The checker validates review shape, candidate inventory, material finding
eligibility, authority packet/clearance/veto coverage, evidence refs,
change-agenda consistency, all-candidate acceptance skew, and handoff safety.
It cannot prove semantic correctness, but it blocks incomplete or over-selected
adversarial reviews before downstream remediation.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ALLOWED_FINDING_CLASS = {
    "current-owned-defect",
    "proof-surface-false-positive",
    "broken-soundness-obligation",
    "illegal-state-admitted",
    "hazardous-footgun",
    "compatibility-break",
    "security-safety-risk",
    "data-loss-risk",
    "verification-gap",
    "complexity-regression",
    "direction-mismatch",
}
ALLOWED_AGENDA_DECISION = {"change-now", "validate-first", "proof-only", "defer", "no-finding", "blocked"}
ALLOWED_POSTURE = {"validating-check-only", "accretive-remediation", "structural-remediation", "proof-only", "no-change", "blocked"}
ALLOWED_BOOL = {"yes", "no", "unknown"}
ALLOWED_ELIGIBLE = {"yes", "no", "blocked"}
CLEARANCE_VALUES = {"clear", "veto", "unresolved", "not-needed", "not-in-scope"}
SKEPTIC_VALUES = {"defeated", "veto", "unresolved", "not-needed"}
AUTHORITY_STATUS = {"cleared-for-finding", "cleared-for-validation", "proof-only", "defer", "no-finding", "blocked"}
PACKET_STATUS = {"accepted", "rejected", "root-equivalent"}
REQUIRED_ROLES = {
    "evidence-authority",
    "soundness-authority",
    "invariant-scope-authority",
    "hazard-footgun-authority",
    "complexity-remediation-authority",
    "verification-authority",
    "finding-skeptic",
}
REQUIRED_SECTIONS = [
    "Review Basis",
    "Review Surface Inventory",
    "Candidate Finding Inventory",
    "Material Findings",
    "Finding Eligibility Tests",
    "Authority Packet Receipts",
    "Authority Clearance Matrix",
    "Authority Veto Ledger",
    "Soundness Ledger",
    "Complexity Delta",
    "Invariant Ledger",
    "Foot-Gun Register",
    "Non-Finding Ledger",
    "Verification Gaps",
    "Residual Uncertainty",
    "Change Agenda",
    "Acceptance Skew Audit",
    "Fixed-Point Judgment",
    "Reviewer Gate",
    "Reviewer Bottom Line",
]
OPTIONAL_SINGLETON_SECTIONS = {"All-Candidate Accepted Justification"}
REQUIRED_GATE_FIELDS = [
    "artifactstatecoverage",
    "reviewsurfacecoverage",
    "candidateinventorycoverage",
    "findingeligibilitycoverage",
    "authoritypacketcoverage",
    "authorityclearancecoverage",
    "authorityvetocoverage",
    "evidencerefcoverage",
    "nonfindingcoverage",
    "verificationpathcoverage",
    "changeagendaconsistency",
    "acceptanceskewaudit",
    "fixedpointjudgmentcoverage",
    "reviewercomplete",
    "changeagendaallowed",
    "implementationhandoffallowed",
    "validationhandoffallowed",
]
ALL_CANDIDATE_CHECKS = {
    "unsupportedalternative": "unsupported alternative",
    "outofscopealternative": "out-of-scope alternative",
    "verificationonlyalternative": "verification-only alternative",
    "wronglayeralternative": "wrong-layer alternative",
    "lowvaluealternative": "low-value alternative",
    "complexitybroadeningcheck": "complexity/broadening check",
    "fresheyesdisagreement": "fresh-eyes disagreement",
}
EMPTY_MARKERS = {"", "-", "—", "n/a", "na", "unknown", "missing", "none", "[]"}
GENERIC_EVIDENCE = {"code", "tests", "review", "looks-right", "artifact", "current-artifacts", "todo"}

COLUMN_ALIASES = {
    "id": "id", "findingid": "id", "candidateid": "id",
    "severity": "severity",
    "findingclass": "findingclass", "class": "findingclass",
    "claim": "claim",
    "agendadecision": "decision", "decision": "decision",
    "evidenceofdefect": "defect", "defectevidence": "defect", "evidence": "defect",
    "evidenceofremedy": "remedy", "remedyevidence": "remedy",
    "confidence": "confidence",
    "minimumacceptablefix": "minfix", "minfix": "minfix",
    "donotbroadeninto": "nobroaden", "nobroaden": "nobroaden",
    "remediationposture": "posture", "posture": "posture",
}
ELIGIBILITY_ALIASES = {
    "id": "id", "findingid": "id", "candidateid": "id",
    "grounded": "grounded", "material": "material", "current": "current",
    "ownership": "ownership", "owned": "ownership",
    "remedyshaped": "remedyshaped", "remedyshaped": "remedyshaped",
    "verificationpath": "verificationpath", "verification": "verificationpath",
    "nofindingdefeated": "nofindingdefeated", "countercasedefeated": "nofindingdefeated",
    "eligible": "eligible",
    "minevidencetochange": "minevidence", "minimumevidencetochange": "minevidence", "minevidencetochangemind": "minevidence", "minimumevidencetochangemind": "minevidence", "minevidence": "minevidence",
}
AUTHORITY_ALIASES = {
    "id": "id", "findingid": "id", "candidateid": "id",
    "evidence": "evidence",
    "soundness": "soundness",
    "invariantscope": "invariantscope", "scope": "invariantscope", "ownership": "invariantscope",
    "hazardfootgun": "hazard", "hazard": "hazard", "footgun": "hazard",
    "complexityremediation": "complexity", "complexity": "complexity", "remediation": "complexity",
    "verification": "verification",
    "findingskeptic": "skeptic", "skeptic": "skeptic",
    "authoritystatus": "status", "status": "status",
    "packetrefs": "packetrefs", "packets": "packetrefs",
}
RECEIPT_ALIASES = {
    "role": "role",
    "packetstatus": "status", "status": "status",
    "artifactstatematch": "artifactmatch",
    "scopematch": "scopematch",
    "candidatescovered": "covered",
    "findingadded": "findingadded",
    "vetoadded": "vetoadded",
    "usedfor": "usedfor",
    "reason": "reason",
}
AGENDA_ALIASES = {
    "id": "id", "findingid": "id", "candidateid": "id",
    "agendadecision": "decision", "decision": "decision",
    "change": "change",
    "prooforvalidationrequired": "proof", "proof": "proof", "validation": "proof",
    "next": "next", "nextaction": "next",
    "remediationposture": "posture", "posture": "posture",
}
GATE_ALIASES = {
    "artifactstatecoverage": "artifactstatecoverage",
    "reviewsurfacecoverage": "reviewsurfacecoverage",
    "candidateinventorycoverage": "candidateinventorycoverage",
    "findingeligibilitycoverage": "findingeligibilitycoverage",
    "authoritypacketcoverage": "authoritypacketcoverage",
    "authorityclearancecoverage": "authorityclearancecoverage",
    "authorityvetocoverage": "authorityvetocoverage",
    "evidencerefcoverage": "evidencerefcoverage",
    "nonfindingcoverage": "nonfindingcoverage",
    "verificationpathcoverage": "verificationpathcoverage",
    "changeagendaconsistency": "changeagendaconsistency",
    "acceptanceskewaudit": "acceptanceskewaudit",
    "fixedpointjudgmentcoverage": "fixedpointjudgmentcoverage",
    "reviewercomplete": "reviewercomplete",
    "changeagendaallowed": "changeagendaallowed",
    "implementationhandoffallowed": "implementationhandoffallowed",
    "validationhandoffallowed": "validationhandoffallowed",
}
INVENTORY_ALIASES = {
    "candidatecount": "candidatecount",
    "materialfindingcount": "materialcount",
    "nonfindingcount": "nonfindingcount",
    "validationitemcount": "validationcount",
    "proofonlycount": "proofonlycount",
    "candidateids": "candidateids",
    "materialfindingids": "materialids",
    "nonfindingids": "nonfindingids",
    "validationitemids": "validationids",
    "proofonlyids": "proofonlyids",
    "missingcandidateids": "missingids",
    "duplicatecandidateids": "duplicateids",
}


def norm_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.strip().lower())


def norm_value(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[`*_]", "", value)
    value = re.sub(r"\s+", "-", value)
    return value


def section_count(text: str, title: str) -> int:
    return len(re.findall(rf"(?im)^\s*#+\s+{re.escape(title)}\s*$", text))


def section_text(text: str, title: str) -> str:
    m = re.search(rf"(?im)^\s*#+\s+{re.escape(title)}\s*$", text)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"(?m)^\s*#+\s+", text[start:])
    end = start + nxt.start() if nxt else len(text)
    return text[start:end].strip()


def split_md_row(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_sep(cells: Sequence[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c.strip()) for c in cells)


def extract_first_table(block: str) -> Tuple[List[str], List[Dict[str, str]]]:
    table=[]; started=False
    for line in block.splitlines():
        if line.strip().startswith('|'):
            table.append(line.rstrip()); started=True
        elif started and not line.strip():
            break
        elif started:
            break
    if len(table)<2: return [],[]
    headers=split_md_row(table[0]); sep=split_md_row(table[1])
    if not is_sep(sep): return [],[]
    rows=[]
    for line in table[2:]:
        cells=split_md_row(line)
        if len(cells)<len(headers): cells += ['']*(len(headers)-len(cells))
        rows.append({headers[i]: cells[i] for i in range(len(headers))})
    return headers, rows


def normalize_rows(headers, rows, aliases):
    hmap={}
    for h in headers:
        c=aliases.get(norm_key(h))
        if c: hmap[c]=h
    out=[]
    for r in rows:
        out.append({c:r.get(h,'').strip() for c,h in hmap.items()})
    return hmap,out


def is_empty(v: str) -> bool:
    return norm_value(v or '') in EMPTY_MARKERS


def evidence_ref_is_concrete(value: str, allow_missing: bool=False) -> bool:
    if allow_missing and norm_value(value) in {"missing", "blocked", "unknown"}:
        return True
    if is_empty(value): return False
    n=norm_value(value)
    if n in GENERIC_EVIDENCE: return False
    if re.search(r"[\w./-]+:\d+", value): return True
    if any(tok in n for tok in ["test", "ci", "cmd", "command", "log", "thread", "pr#", "github", "diff", "src/", "tests/", "commit", "spec", "docs/"]): return True
    if "/" in value or "." in value or "#" in value: return True
    return len(value.strip()) >= 16


def parse_int(v: str) -> Optional[int]:
    m=re.search(r"-?\d+", v or '')
    return int(m.group(0)) if m else None


def parse_id_list(v: str) -> List[str]:
    if is_empty(v): return []
    v=re.sub(r"^[\[({]", "", v.strip())
    v=re.sub(r"[\])}]$", "", v)
    return [p.strip().strip('"\'`') for p in re.split(r"[,;\s]+", v) if p.strip().strip('"\'`')]


def parse_inventory(block: str) -> Dict[str,str]:
    out={}
    for line in block.splitlines():
        s=re.sub(r"^[-*]\s+", "", line.strip())
        if ':' not in s: continue
        k,v=s.split(':',1)
        c=INVENTORY_ALIASES.get(norm_key(k))
        if c: out[c]=v.strip()
    return out


def rows_by_id(rows):
    return {r.get('id','').strip(): r for r in rows if r.get('id','').strip()}


def validate_structured_table(text, title, checks, errors):
    if section_count(text,title)!=1:
        errors.append(f"missing required section: {title}")
        return
    h,raw=extract_first_table(section_text(text,title))
    if not raw:
        errors.append(f"{title} must be a structured table")
        return
    heads={norm_key(x): x for x in h}
    ch=heads.get('check'); rh=heads.get('result') or heads.get('status') or heads.get('value')
    eh=heads.get('evidenceref') or heads.get('evidence')
    wh=heads.get('why') or heads.get('basis') or heads.get('whywarranted')
    if not all([ch,rh,eh,wh]):
        errors.append(f"{title} missing check/result/evidence ref/why columns")
        return
    seen={norm_key(r.get(ch,'')): r for r in raw}
    for key,label in checks.items():
        if key not in seen:
            errors.append(f"{title} missing check `{label}`")
            continue
        row=seen[key]
        if norm_value(row.get(rh,''))!='pass': errors.append(f"{title} `{label}` must pass")
        if not evidence_ref_is_concrete(row.get(eh,'')): errors.append(f"{title} `{label}` requires concrete evidence ref")
        if is_empty(row.get(wh,'')): errors.append(f"{title} `{label}` requires explanation")


def normalize_gate(headers, rows):
    if not headers: return {}
    fh=vh=None
    for h in headers:
        k=norm_key(h)
        if k in {'field','check','gatefield'}: fh=h
        if k in {'value','status','result'}: vh=h
    if fh is None or vh is None:
        if len(headers)>=2: fh,vh=headers[0],headers[1]
        else: return {}
    out={}
    for r in rows:
        c=GATE_ALIASES.get(norm_key(r.get(fh,'')))
        if c: out[c]=norm_value(r.get(vh,''))
    return out

@dataclass
class CheckResult:
    passed: bool
    errors: List[str]=field(default_factory=list)
    warnings: List[str]=field(default_factory=list)
    stats: Dict[str,int]=field(default_factory=dict)
    gate: Dict[str,str]=field(default_factory=dict)
    def to_json(self):
        return json.dumps({'passed': self.passed, 'errors': self.errors, 'warnings': self.warnings, 'stats': self.stats, 'gate': self.gate}, indent=2, sort_keys=True)


def check_review(text: str) -> CheckResult:
    errors=[]; warnings=[]
    for sec in REQUIRED_SECTIONS:
        c=section_count(text,sec)
        if c!=1: errors.append(f"{sec} must appear exactly once, found {c}")
    for sec in OPTIONAL_SINGLETON_SECTIONS:
        c=section_count(text,sec)
        if c>1: errors.append(f"{sec} must appear at most once, found {c}")

    basis=section_text(text,'Review Basis')
    if 'artifact_state_id' not in basis: errors.append('Review Basis missing artifact_state_id')
    for key in ['branch','head','diff_digest','review_surface_digest','ci_state']:
        if basis and not re.search(rf"(?im)^\s*{re.escape(key)}\s*:", basis):
            errors.append(f"artifact_state_id missing `{key}`")

    inv=parse_inventory(section_text(text,'Candidate Finding Inventory'))
    for k in ['candidatecount','materialcount','nonfindingcount','validationcount','proofonlycount','candidateids','materialids','nonfindingids','validationids','proofonlyids','missingids','duplicateids']:
        if k not in inv: errors.append(f"Candidate Finding Inventory missing `{k}`")
    candidate_ids=parse_id_list(inv.get('candidateids',''))
    material_ids_decl=parse_id_list(inv.get('materialids',''))
    nonfinding_ids=parse_id_list(inv.get('nonfindingids',''))
    validation_ids=parse_id_list(inv.get('validationids',''))
    proofonly_ids=parse_id_list(inv.get('proofonlyids',''))
    missing_ids=parse_id_list(inv.get('missingids',''))
    duplicate_ids=parse_id_list(inv.get('duplicateids',''))
    if missing_ids: errors.append('Candidate inventory reports missing ids: '+', '.join(missing_ids))
    if duplicate_ids: errors.append('Candidate inventory reports duplicate ids: '+', '.join(duplicate_ids))

    fh, fr_raw=extract_first_table(section_text(text,'Material Findings'))
    fmap, findings=normalize_rows(fh, fr_raw, COLUMN_ALIASES)
    for field in ['id','severity','findingclass','claim','decision','defect','remedy','confidence','minfix','nobroaden','posture']:
        if field not in fmap: errors.append('Material Findings missing required column: '+field)
    fids=[r.get('id','').strip() for r in findings if r.get('id','').strip()]
    if len(fids)!=len(set(fids)): errors.append('Material Findings duplicate ids')
    if set(material_ids_decl)!=set(fids): errors.append('Candidate inventory material_finding_ids does not match Material Findings ids')

    eh, er_raw=extract_first_table(section_text(text,'Finding Eligibility Tests'))
    emap, elig_rows=normalize_rows(eh, er_raw, ELIGIBILITY_ALIASES)
    for field in ['id','grounded','material','current','ownership','remedyshaped','verificationpath','nofindingdefeated','eligible','minevidence']:
        if field not in emap: errors.append('Finding Eligibility Tests missing required column: '+field)
    elig=rows_by_id(elig_rows)

    rh, rr_raw=extract_first_table(section_text(text,'Authority Packet Receipts'))
    rmap, receipts=normalize_rows(rh, rr_raw, RECEIPT_ALIASES)
    for field in ['role','status','artifactmatch','scopematch','covered','findingadded','vetoadded','usedfor','reason']:
        if field not in rmap: errors.append('Authority Packet Receipts missing required column: '+field)
    covered_roles=set()
    for row in receipts:
        role=norm_value(row.get('role',''))
        status=norm_value(row.get('status',''))
        if status not in PACKET_STATUS: errors.append(f"Authority Packet Receipts invalid status `{row.get('status','')}`")
        if norm_value(row.get('artifactmatch',''))!='yes': errors.append(f"{role}: authority packet requires artifact state match yes")
        if norm_value(row.get('scopematch',''))!='yes': errors.append(f"{role}: authority packet requires scope match yes")
        if status in {'accepted','root-equivalent'}: covered_roles.add(role)
        if is_empty(row.get('reason','')): errors.append(f"{role}: authority receipt requires reason")
    if fids and not REQUIRED_ROLES.issubset(covered_roles):
        errors.append('Authority Packet Receipts missing accepted/root-equivalent roles: '+', '.join(sorted(REQUIRED_ROLES-covered_roles)))

    ah, ar_raw=extract_first_table(section_text(text,'Authority Clearance Matrix'))
    amap, auth_rows=normalize_rows(ah, ar_raw, AUTHORITY_ALIASES)
    for field in ['id','evidence','soundness','invariantscope','hazard','complexity','verification','skeptic','status','packetrefs']:
        if field not in amap: errors.append('Authority Clearance Matrix missing required column: '+field)
    auth=rows_by_id(auth_rows)

    vh, vr_raw=extract_first_table(section_text(text,'Authority Veto Ledger'))
    # Veto table can be empty only if header exists; if rows present, verify concrete evidence unless final route is cleared.
    for row in vr_raw:
        cells={norm_key(k):v for k,v in row.items()}
        vid=next((v for k,v in cells.items() if k in {'id','findingid','candidateid'}), '')
        evidence=next((v for k,v in cells.items() if k in {'evidenceref','evidence'}), '')
        final=norm_value(next((v for k,v in cells.items() if k in {'finalroute','route'}), ''))
        if vid and final not in {'cleared-for-finding','change-now'} and not evidence_ref_is_concrete(evidence, allow_missing=True):
            errors.append(f"{vid}: veto row requires concrete evidence ref or explicit missing marker")

    ag_h, ag_raw=extract_first_table(section_text(text,'Change Agenda'))
    ag_map, agenda_rows=normalize_rows(ag_h, ag_raw, AGENDA_ALIASES)
    for field in ['id','decision','change','proof','next','posture']:
        if field not in ag_map: errors.append('Change Agenda missing required column: '+field)
    agenda=rows_by_id(agenda_rows)

    for rid in candidate_ids:
        if rid not in auth: errors.append(f"{rid}: missing Authority Clearance Matrix row")
        if rid not in elig: errors.append(f"{rid}: missing Finding Eligibility Tests row")
    for rid in fids:
        row=next(r for r in findings if r.get('id','').strip()==rid)
        decision=norm_value(row.get('decision',''))
        fclass=norm_value(row.get('findingclass',''))
        posture=norm_value(row.get('posture',''))
        if fclass not in ALLOWED_FINDING_CLASS: errors.append(f"{rid}: invalid finding class `{row.get('findingclass','')}`")
        if decision not in {'change-now','validate-first'}: errors.append(f"{rid}: material finding agenda decision must be change-now or validate-first")
        if posture not in ALLOWED_POSTURE: errors.append(f"{rid}: invalid remediation posture `{row.get('posture','')}`")
        if not evidence_ref_is_concrete(row.get('defect','')): errors.append(f"{rid}: material finding requires concrete evidence of defect")
        if decision=='change-now' and not evidence_ref_is_concrete(row.get('remedy','')): errors.append(f"{rid}: change-now finding requires concrete evidence of remedy")
        if decision=='validate-first' and posture!='validating-check-only': errors.append(f"{rid}: validate-first requires validating-check-only posture")
        if is_empty(row.get('minfix','')): errors.append(f"{rid}: missing minimum acceptable fix")
        if is_empty(row.get('nobroaden','')): errors.append(f"{rid}: missing do_not_broaden_into")
        e=elig.get(rid,{})
        for field in ['grounded','material','current','ownership','remedyshaped','verificationpath','nofindingdefeated']:
            if norm_value(e.get(field,''))!='yes': errors.append(f"{rid}: material finding requires {field}=yes")
        if norm_value(e.get('eligible',''))!='yes': errors.append(f"{rid}: material finding requires eligible=yes")
        if is_empty(e.get('minevidence','')): errors.append(f"{rid}: missing min evidence to change mind")
        a=auth.get(rid,{})
        status=norm_value(a.get('status',''))
        if decision=='change-now' and status!='cleared-for-finding': errors.append(f"{rid}: change-now requires authority status cleared-for-finding")
        if decision=='validate-first' and status!='cleared-for-validation': errors.append(f"{rid}: validate-first requires authority status cleared-for-validation")
        for field in ['evidence','soundness','invariantscope','hazard','complexity','verification']:
            val=norm_value(a.get(field,''))
            if val not in CLEARANCE_VALUES: errors.append(f"{rid}: invalid authority clearance {field}={val}")
            if val in {'veto','unresolved'} and decision=='change-now': errors.append(f"{rid}: change-now cannot have {field}={val}")
        sk=norm_value(a.get('skeptic',''))
        if sk not in SKEPTIC_VALUES: errors.append(f"{rid}: invalid finding skeptic clearance `{sk}`")
        if sk!='defeated': errors.append(f"{rid}: material finding requires finding skeptic defeated")
        if is_empty(a.get('packetrefs','')): errors.append(f"{rid}: authority matrix requires packet refs")
        if rid not in agenda: errors.append(f"{rid}: material finding missing Change Agenda row")

    agenda_ids=set(agenda)
    if agenda_ids - set(fids): errors.append('Change Agenda contains ids not in Material Findings: '+', '.join(sorted(agenda_ids-set(fids))))
    for rid,row in agenda.items():
        decision=norm_value(row.get('decision',''))
        if decision not in {'change-now','validate-first'}: errors.append(f"{rid}: Change Agenda decision must be change-now or validate-first")
        if not evidence_ref_is_concrete(row.get('proof','')): errors.append(f"{rid}: Change Agenda requires concrete proof or validation required")
        if is_empty(row.get('change','')) or is_empty(row.get('next','')): errors.append(f"{rid}: Change Agenda requires change and next")

    # Non-finding/proof-only/validation inventory consistency
    if set(candidate_ids) - (set(fids)|set(nonfinding_ids)|set(validation_ids)|set(proofonly_ids)):
        errors.append('Candidate ids missing from material/non-finding/validation/proof buckets: '+', '.join(sorted(set(candidate_ids)-(set(fids)|set(nonfinding_ids)|set(validation_ids)|set(proofonly_ids)))))
    if nonfinding_ids and not section_text(text,'Non-Finding Ledger').strip(): errors.append('Non-Finding Ledger empty despite non_finding_ids')

    # All-candidate accepted/selected warning
    candidate_count=parse_int(inv.get('candidatecount',''))
    material_count=parse_int(inv.get('materialcount',''))
    validation_count=parse_int(inv.get('validationcount','')) or 0
    if candidate_count is not None and candidate_count>0 and material_count is not None:
        if material_count + validation_count == candidate_count:
            validate_structured_table(text, 'All-Candidate Accepted Justification', ALL_CANDIDATE_CHECKS, errors)

    gh, gr=extract_first_table(section_text(text,'Reviewer Gate'))
    gate=normalize_gate(gh, gr)
    missing=[f for f in REQUIRED_GATE_FIELDS if f not in gate]
    if missing: errors.append('Reviewer Gate missing required fields: '+', '.join(missing))
    for f in REQUIRED_GATE_FIELDS:
        if f not in gate: continue
        v=gate[f]
        if f in {'changeagendaallowed','implementationhandoffallowed','validationhandoffallowed'}:
            if v not in {'yes','no'}: errors.append(f"{f} must be yes/no, got `{v}`")
        elif v not in {'pass','fail'}:
            errors.append(f"{f} must be pass/fail, got `{v}`")
    fail_fields=[f for f in REQUIRED_GATE_FIELDS if f not in {'changeagendaallowed','implementationhandoffallowed','validationhandoffallowed'} and gate.get(f)=='fail']
    if fail_fields and gate.get('reviewercomplete')=='pass': errors.append('reviewer_complete is pass despite failed gate fields: '+', '.join(fail_fields))
    if errors and gate.get('reviewercomplete')=='pass': errors.append('reviewer_complete is pass despite mechanical contract errors')
    if gate.get('implementationhandoffallowed')=='yes': errors.append('implementation_handoff_allowed must be no for adversarial-reviewer')
    if gate.get('changeagendaallowed')=='yes' and not fids: errors.append('change_agenda_allowed yes but no material findings')
    if errors and gate.get('changeagendaallowed')=='yes': errors.append('change_agenda_allowed yes despite mechanical contract errors')
    if (fail_fields or errors) and 'blocked' not in section_text(text,'Reviewer Bottom Line').lower(): errors.append('failed gate or mechanical error requires blocked Reviewer Bottom Line')
    if not section_text(text,'Acceptance Skew Audit').strip(): errors.append('Acceptance Skew Audit is empty')
    if not section_text(text,'Fixed-Point Judgment').strip(): errors.append('Fixed-Point Judgment is empty')

    stats={
        'candidates': len(candidate_ids),
        'material_findings': len(fids),
        'agenda_items': len(agenda_rows),
        'non_findings': len(nonfinding_ids),
        'validation_items': len(validation_ids),
        'errors': len(errors),
        'warnings': len(warnings),
    }
    return CheckResult(not errors, errors, warnings, stats, gate)


def valid_fixture() -> str:
    return """
## Review Basis

artifact_state_id:
  branch: feature/retry
  base: main@abc123
  head: feature@def456
  diff_digest: paths=src/a.py,tests/test_a.py
  review_surface_digest: src/a.py,tests/test_a.py
  ci_state: local pytest pass 2026-05-29

## Review Surface Inventory

- artifact_state_id: feature@def456
- review_surface_id: retry-review
- artifact_set: src/a.py, tests/test_a.py
- changed_files: src/a.py
- nearby_files_checked: tests/test_a.py
- proof_surfaces_checked: pytest tests/test_a.py
- direction_sources_checked: PR body retry idempotence
- limits_or_unavailable_evidence: none

## Candidate Finding Inventory

- candidate_count: 2
- material_finding_count: 1
- non_finding_count: 1
- validation_item_count: 0
- proof_only_count: 0
- candidate_ids: F1,F2
- material_finding_ids: F1
- non_finding_ids: F2
- validation_item_ids: []
- proof_only_ids: []
- missing_candidate_ids: []
- duplicate_candidate_ids: []

## Material Findings

| id | severity | finding class | claim | agenda decision | evidence of defect | evidence of remedy | confidence | minimum acceptable fix | do not broaden into | remediation posture |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 | high | current-owned-defect | retry can write twice | change-now | src/a.py:10 | tests/test_a.py::test_retry_idempotent | high | add idempotence guard and regression test | do not rewrite queue subsystem | accretive-remediation |

## Finding Eligibility Tests

| id | grounded | material | current | ownership | remedy-shaped | verification-path | no-finding defeated | eligible | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|---|
| F1 | yes | yes | yes | yes | yes | yes | yes | yes | proof existing guard prevents duplicate write |
| F2 | no | no | yes | no | no | yes | no | no | repo convention requiring rename |

## Authority Packet Receipts

| role | packet status | artifact state match | scope match | candidates covered | finding added | veto added | used for | reason |
|---|---|---|---|---|---|---|---|---|
| evidence-authority | root-equivalent | yes | yes | F1,F2 | F1 | F2 | grounding | local artifact refs |
| soundness-authority | root-equivalent | yes | yes | F1,F2 | F1 | F2 | soundness | duplicate write breaks idempotence |
| invariant-scope-authority | root-equivalent | yes | yes | F1,F2 | F1 | F2 | ownership | retry PR owns idempotence |
| hazard-footgun-authority | root-equivalent | yes | yes | F1,F2 | F1 | F2 | hazards | duplicate write is material |
| complexity-remediation-authority | root-equivalent | yes | yes | F1,F2 | F1 | F2 | remedy breadth | narrow guard sufficient |
| verification-authority | root-equivalent | yes | yes | F1,F2 | F1 | F2 | proof path | regression test named |
| finding-skeptic | root-equivalent | yes | yes | F1,F2 | F1 | F2 | no-finding case | F1 defeated, F2 preserved |

## Authority Clearance Matrix

| id | evidence | soundness | invariant/scope | hazard/footgun | complexity/remediation | verification | finding skeptic | authority status | packet refs |
|---|---|---|---|---|---|---|---|---|
| F1 | clear | clear | clear | clear | clear | clear | defeated | cleared-for-finding | evidence:F1,soundness:F1,scope:F1,verification:F1,skeptic:F1 |
| F2 | veto | not-needed | veto | not-needed | not-needed | clear | veto | no-finding | evidence:F2,scope:F2,skeptic:F2 |

## Authority Veto Ledger

| id | veto source | veto class | veto claim | evidence ref | required to clear | final route |
|---|---|---|---|---|---|---|
| F2 | finding-skeptic | low-value | rename is preference-only | src/a.py:1 | repo naming convention | no-finding |

## Soundness Ledger

- F1: retry idempotence broken; witness src/a.py:10; proof tests/test_a.py::test_retry_idempotent.

## Complexity Delta

- F1 is accretive; no structural broadening.

## Invariant Ledger

- retry idempotence: broken by F1, owned by PR.

## Foot-Gun Register

- duplicate write foot-gun is material and detectable by regression.

## Non-Finding Ledger

- F2: rename request is preference-only; no convention-backed defect.

## Verification Gaps

- none for F1 after named regression.

## Residual Uncertainty

- fresh-eyes pass found no material delta.

## Change Agenda

| id | agenda decision | change | proof or validation required | next | remediation posture |
|---|---|---|---|---|---|
| F1 | change-now | add idempotence guard | tests/test_a.py::test_retry_idempotent | route to implementer after separate intake | accretive-remediation |

## Acceptance Skew Audit

- candidate distribution: material=1, non-finding=1
- all-candidate pressure checked: not all accepted
- no-finding pressure: F2 preserved

## Fixed-Point Judgment

Not fixed-point ready until F1 is addressed and regression passes.

## Reviewer Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass | artifact state recorded |
| review_surface_coverage | pass | reviewed paths named |
| candidate_inventory_coverage | pass | candidates match ledgers |
| finding_eligibility_coverage | pass | all candidates have eligibility rows |
| authority_packet_coverage | pass | all roles root-equivalent |
| authority_clearance_coverage | pass | all candidates have authority rows |
| authority_veto_coverage | pass | F2 veto represented and respected |
| evidence_ref_coverage | pass | F1 has concrete refs |
| non_finding_coverage | pass | F2 listed |
| verification_path_coverage | pass | F1 proof path named |
| change_agenda_consistency | pass | agenda equals material finding F1 |
| acceptance_skew_audit | pass | skew audited |
| fixed_point_judgment_coverage | pass | judgment present |
| reviewer_complete | pass | all required fields pass |
| change_agenda_allowed | yes | F1 cleared |
| implementation_handoff_allowed | no | adversarial-reviewer does not implement |
| validation_handoff_allowed | no | no validate-first items |

## Reviewer Bottom Line

Proceed with separate remediation intake for F1 only; F2 is not a finding.
"""


def invalid_fixture() -> str:
    return """
## Review Basis

artifact_state_id:
  branch: feature/retry

## Review Surface Inventory

- artifact_state_id: unknown

## Candidate Finding Inventory

- candidate_count: 1
- material_finding_count: 1
- non_finding_count: 0
- validation_item_count: 0
- proof_only_count: 0
- candidate_ids: F1
- material_finding_ids: F1
- non_finding_ids: []
- validation_item_ids: []
- proof_only_ids: []
- missing_candidate_ids: []
- duplicate_candidate_ids: []

## Material Findings

| id | severity | finding class | claim | agenda decision | evidence of defect | evidence of remedy | confidence | minimum acceptable fix | do not broaden into | remediation posture |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 | high | current-owned-defect | seems unsafe | change-now | code | tests | high | fix it | none | structural-remediation |

## Finding Eligibility Tests

| id | grounded | material | current | ownership | remedy-shaped | verification-path | no-finding defeated | eligible | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|---|
| F1 | unknown | yes | unknown | unknown | no | no | unresolved | yes | proof |

## Authority Packet Receipts

| role | packet status | artifact state match | scope match | candidates covered | finding added | veto added | used for | reason |
|---|---|---|---|---|---|---|---|---|
| evidence-authority | rejected | no | no | F1 | F1 | none | grounding | stale |

## Authority Clearance Matrix

| id | evidence | soundness | invariant/scope | hazard/footgun | complexity/remediation | verification | finding skeptic | authority status | packet refs |
|---|---|---|---|---|---|---|---|---|
| F1 | unresolved | clear | unknown | clear | clear | unresolved | unresolved | cleared-for-finding | none |

## Authority Veto Ledger

| id | veto source | veto class | veto claim | evidence ref | required to clear | final route |
|---|---|---|---|---|---|---|

## Soundness Ledger
none.
## Complexity Delta
none.
## Invariant Ledger
none.
## Foot-Gun Register
none.
## Non-Finding Ledger
none.
## Verification Gaps
none.
## Residual Uncertainty
none.
## Change Agenda

| id | agenda decision | change | proof or validation required | next | remediation posture |
|---|---|---|---|---|---|
| F1 | change-now | fix it | tests | implement | structural-remediation |

## Acceptance Skew Audit
all accepted.

## Fixed-Point Judgment
ready.

## Reviewer Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | fail | missing |
| review_surface_coverage | fail | missing |
| candidate_inventory_coverage | pass | one id |
| finding_eligibility_coverage | fail | weak |
| authority_packet_coverage | fail | missing roles |
| authority_clearance_coverage | fail | unresolved |
| authority_veto_coverage | fail | none |
| evidence_ref_coverage | fail | generic |
| non_finding_coverage | fail | none |
| verification_path_coverage | fail | generic |
| change_agenda_consistency | fail | unsafe |
| acceptance_skew_audit | fail | generic |
| fixed_point_judgment_coverage | pass | present |
| reviewer_complete | pass | wrong |
| change_agenda_allowed | yes | wrong |
| implementation_handoff_allowed | yes | wrong |
| validation_handoff_allowed | no | none |

## Reviewer Bottom Line

Proceed.
"""


def run_self_test() -> int:
    good=check_review(valid_fixture())
    bad=check_review(invalid_fixture())
    if good.passed and not bad.passed:
        print('self-test passed')
        return 0
    print('self-test failed')
    print('valid result:', good.to_json())
    print('invalid result:', bad.to_json())
    return 1


def print_human(result: CheckResult) -> None:
    print('PASS: Authority-Gated v1 adversarial review contract satisfied' if result.passed else 'FAIL: Authority-Gated v1 adversarial review contract incomplete')
    print('stats:', ', '.join(f"{k}={v}" for k,v in result.stats.items()))
    if result.gate:
        print('gate:', ', '.join(f"{k}={v}" for k,v in result.gate.items()))
    if result.errors:
        print('errors:')
        for e in result.errors: print('-', e)
    if result.warnings:
        print('warnings:')
        for w in result.warnings: print('-', w)


def main(argv: Optional[Sequence[str]]=None) -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('path', nargs='?', help='Markdown adversarial review output to check')
    ap.add_argument('--json', action='store_true', help='emit JSON result')
    ap.add_argument('--self-test', action='store_true', help='run built-in self-test')
    args=ap.parse_args(argv)
    if args.self_test: return run_self_test()
    if not args.path: ap.error('path is required unless --self-test is used')
    try:
        text=Path(args.path).read_text(encoding='utf-8')
    except OSError as exc:
        print(f'error reading {args.path}: {exc}', file=sys.stderr)
        return 2
    result=check_review(text)
    print(result.to_json() if args.json else '', end='') if args.json else print_human(result)
    return 0 if result.passed else 2

if __name__ == '__main__':
    raise SystemExit(main())

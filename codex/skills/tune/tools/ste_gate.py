#!/usr/bin/env python3
"""Validate skill_tuning_evidence / STE-v1."""

from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any

KINDS={"decision","execution","evidence","orchestration","mixed"}
AUTHORITIES={"explicit","inferred","absent"}

def load(path: str) -> dict[str, Any]:
    text=sys.stdin.read() if path=="-" else Path(path).read_text(encoding="utf-8")
    value=json.loads(text)
    if not isinstance(value,dict): raise ValueError("packet must be an object")
    return value.get("skill_tuning_evidence",value)

def nonnegative_int(obj: dict[str,Any], key: str, errors: list[str], prefix: str) -> int:
    v=obj.get(key)
    if not isinstance(v,int) or v<0:
        errors.append(f"{prefix}.{key}:must-be-nonnegative-int")
        return 0
    return v

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("file")
    args=parser.parse_args()
    errors=[]; warnings=[]
    try: packet=load(args.file)
    except Exception as exc:
        print(json.dumps({"ste_gate":{"verdict":"fail","errors":[str(exc)]}},indent=2)); return 1
    if packet.get("packet_version")!="STE-v1": errors.append("packet_version")
    if not packet.get("target_skill"): errors.append("target_skill")
    if packet.get("target_kind") not in KINDS: errors.append("target_kind")
    contract=packet.get("contract",{})
    if not isinstance(contract,dict): errors.append("contract:object"); contract={}
    if contract.get("authority") not in AUTHORITIES: errors.append("contract.authority")
    if contract.get("authority")=="explicit" and not contract.get("fingerprint"): errors.append("contract.fingerprint")
    denom=packet.get("denominator",{})
    if not isinstance(denom,dict): errors.append("denominator:object"); denom={}
    values={k:nonnegative_int(denom,k,errors,"denominator") for k in (
        "candidate_sessions","activation_sessions","decision_episodes",
        "explicit_effect_episodes","associated_outcome_episodes","matched_control_episodes")}
    if values["activation_sessions"]>values["candidate_sessions"]:
        errors.append("denominator:activation_gt_candidate")
    if values["explicit_effect_episodes"]>values["decision_episodes"]:
        errors.append("denominator:explicit_gt_episodes")
    for field in ("trigger_quality","decision_influence","contract_compliance","outcomes","workarounds","recurrent_gap_signatures","exemplars","evidence_limitations"):
        if field not in packet: errors.append(f"{field}:missing")
    if not packet.get("skill_versions_observed"): warnings.append("skill_versions_observed:empty")
    result={"ste_gate":{"verdict":"pass" if not errors else "fail","errors":errors,"warnings":warnings}}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if not errors else 2

if __name__=="__main__":
    raise SystemExit(main())

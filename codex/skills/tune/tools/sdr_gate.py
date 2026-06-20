#!/usr/bin/env python3
"""Validate skill_decision_receipt / SDR-v1."""

from __future__ import annotations
import argparse,json,sys
from pathlib import Path

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("file"); a=p.parse_args()
    try:
        text=sys.stdin.read() if a.file=="-" else Path(a.file).read_text(encoding="utf-8")
        value=json.loads(text)
        body=value.get("skill_decision_receipt",value)
    except Exception as exc:
        print(json.dumps({"sdr_gate":{"verdict":"fail","errors":[str(exc)]}},indent=2)); return 1
    errors=[]
    if body.get("receipt_version")!="SDR-v1": errors.append("receipt_version")
    for field in ("decision_id","skill","question","selected_route","artifact_state"):
        if body.get(field) in (None,"",{}): errors.append(field)
    for field in ("trigger_refs","clause_refs","alternatives_considered","rejected_routes","evidence_refs"):
        if not isinstance(body.get(field,[]),list): errors.append(f"{field}:list")
    if body.get("selected_route") in body.get("rejected_routes",[]): errors.append("selected_route_rejected")
    result={"sdr_gate":{"verdict":"pass" if not errors else "fail","errors":errors}}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if not errors else 2
if __name__=="__main__": raise SystemExit(main())

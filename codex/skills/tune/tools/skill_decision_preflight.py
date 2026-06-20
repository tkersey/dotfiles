#!/usr/bin/env python3
"""Check whether installed seq supports skill-decision-audit."""

from __future__ import annotations
import argparse,json,shutil,subprocess

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--seq",default="seq"); a=p.parse_args()
    path=shutil.which(a.seq)
    result={"skill_decision_preflight":{"binary":path,"supported":False}}
    if not path:
        result["skill_decision_preflight"]["reason"]="seq-not-found"
        print(json.dumps(result,indent=2)); return 2
    proc=subprocess.run([path,"skill-decision-audit","--help"],text=True,capture_output=True)
    result["skill_decision_preflight"]["supported"]=proc.returncode==0
    result["skill_decision_preflight"]["reason"]="supported" if proc.returncode==0 else "command-unavailable"
    print(json.dumps(result,indent=2))
    return 0 if proc.returncode==0 else 2
if __name__=="__main__": raise SystemExit(main())

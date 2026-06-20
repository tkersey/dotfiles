#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"tools"
ASSETS=ROOT/"assets"

def run(tool,*args):
    return subprocess.run([sys.executable,str(TOOLS/tool),*map(str,args)],text=True,capture_output=True)

def main()->int:
    contract=run("decision_contract_lint.py",ASSETS/"decision-contract.example.yaml")
    assert contract.returncode==0, contract.stdout+contract.stderr
    assert json.loads(contract.stdout)["decision_contract_lint"]["verdict"]=="pass"

    ste=run("ste_gate.py",ASSETS/"ste-v1.example.json")
    assert ste.returncode==0, ste.stdout+ste.stderr
    assert json.loads(ste.stdout)["ste_gate"]["verdict"]=="pass"

    sdr=run("sdr_gate.py",ASSETS/"sdr-v1.example.json")
    assert sdr.returncode==0, sdr.stdout+sdr.stderr

    with tempfile.TemporaryDirectory() as td:
        bad=Path(td)/"bad.json"
        packet=json.loads((ASSETS/"ste-v1.example.json").read_text())
        packet["skill_tuning_evidence"]["denominator"]["activation_sessions"]=99
        bad.write_text(json.dumps(packet))
        result=run("ste_gate.py",bad)
        assert result.returncode==2
        assert "activation_gt_candidate" in result.stdout

    print("tune decision-evidence tools: PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())

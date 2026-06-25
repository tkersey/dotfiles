#!/usr/bin/env python3
"""Lint the human proposed-plan projection and embedded EPG-v1."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
TOOLS=Path(__file__).resolve().parents[1]/'tools';sys.path.insert(0,str(TOOLS))
from common import extract_epg_json_from_markdown,read_text
from execution_policy_gate import validate_policy
HEADINGS=['Strategy Summary','Source and Invariants','Current Belief and Critical Unknowns','Commitment Horizon','Policy Branches','Proof, Rollback, and Terminal States','Policy Delta','Execution Policy Graph']
LEGACY=['Iteration Action Log','Iteration Change Log','Iteration Reports','Contract Signals','Implementation Brief']
def match(body,h):return re.search(rf'(?im)^#{{1,6}}\s+{re.escape(h)}\s*$',body)
def section(body,h):
 m=match(body,h)
 if not m:return''
 rest=body[m.end():];n=re.search(r'(?im)^#{1,6}\s+\S',rest);return rest[:n.start() if n else None].strip()
def main()->int:
 p=argparse.ArgumentParser();p.add_argument('--file');p.add_argument('--json',action='store_true');a=p.parse_args();text=read_text(a.file or '-');errors=[];warnings=[]
 try:wrapper,body=extract_epg_json_from_markdown(text);epg=wrapper.get('execution_policy_graph',{})
 except Exception as exc:errors.append(str(exc));body='';epg={}
 if body:
  titles=re.findall(r'(?im)^#\s+\S.+$',body)
  if len(titles)!=1:errors.append('Plan must contain exactly one level-1 title.')
  positions=[]
  for h in HEADINGS:
   m=match(body,h)
   if not m:errors.append(f'Missing required heading: `{h}`.');continue
   positions.append(m.start())
   if not section(body,h):errors.append(f'`{h}` must not be empty.')
  if len(positions)==len(HEADINGS) and positions!=sorted(positions):errors.append('Required headings are out of order.')
  for h in LEGACY:
   if match(body,h):errors.append(f'Legacy heading `{h}` is not part of EPG-v1 output.')
  if re.search(r'(?im)^\s*Iteration:\s*\d+\s*$',body):errors.append('Iteration markers are forbidden.')
  if re.search(r'(?i)unchanged from iteration|same as previous|see above|carry forward',body):errors.append('Carry-forward placeholder found.')
  pe,pw,derived=validate_policy(epg);errors += [f'EPG: {x}' for x in pe];warnings += [f'EPG: {x}' for x in pw]
  summary=section(body,'Strategy Summary');horizon=section(body,'Commitment Horizon');branches=section(body,'Policy Branches');terminal=section(body,'Proof, Rollback, and Terminal States')
  if epg.get('goal',{}).get('objective') and epg['goal']['objective'] not in summary:warnings.append('Strategy Summary does not repeat exact objective.')
  for aid in epg.get('initial_state',{}).get('completed_actions',[]):
   if aid not in horizon:warnings.append(f'Commitment Horizon does not mention completed action {aid}.')
  rules=[r.get('rule_id') for r in epg.get('policy',{}).get('rules',[]) if isinstance(r,dict)]
  if rules and not any(r in branches for r in rules):errors.append('Policy Branches must mention at least one rule ID.')
  if 'terminal:success' not in terminal and 'success' not in terminal.lower():warnings.append('Terminal section does not describe success.')
 else:derived={}
 payload={'plan_contract_lint':{'verdict':'pass' if not errors else 'fail',**derived,'errors':errors,'warnings':warnings}}
 if a.json:print(json.dumps(payload,indent=2,sort_keys=True))
 else:
  for w in warnings:print('[WARN]',w)
  for e in errors:print('[FAIL]',e)
  if not errors:print('[OK] EPG-v1 plan contract checks passed.')
 return 0 if not errors else 1
if __name__=='__main__':raise SystemExit(main())

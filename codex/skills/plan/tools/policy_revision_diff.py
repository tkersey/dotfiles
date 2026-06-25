#!/usr/bin/env python3
"""Compute an artifact-derived EPG revision delta."""
from __future__ import annotations
import argparse
from typing import Any
from common import canonical_digest, emit, load_epg
from execution_policy_gate import validate_policy

def rows(value:Any,key:str)->dict[str,dict[str,Any]]:
 out={}
 if isinstance(value,list):
  for row in value:
   if isinstance(row,dict) and isinstance(row.get(key),str): out[row[key]]=row
 return out

def delta(a,b):
 aa=set(a); bb=set(b)
 return {'added':sorted(bb-aa),'removed':sorted(aa-bb),'changed':sorted(x for x in aa&bb if a[x]!=b[x])}

def main()->int:
 p=argparse.ArgumentParser(); p.add_argument('--parent',required=True);p.add_argument('--current',required=True);p.add_argument('--strict',action='store_true');a=p.parse_args()
 errors=[];warnings=[]
 try:
  parent,_=load_epg(a.parent); current,_=load_epg(a.current)
 except Exception as exc:return emit('policy_revision_diff',{},[str(exc)],[])
 pe,pw,_=validate_policy(parent);ce,cw,_=validate_policy(current);errors += [f'parent:{x}' for x in pe]+[f'current:{x}' for x in ce];warnings += [f'parent:{x}' for x in pw]+[f'current:{x}' for x in cw]
 pd=canonical_digest(parent);cd=canonical_digest(current)
 if parent.get('policy_id')!=current.get('policy_id'):errors.append('policy_id:mismatch')
 if current.get('revision')!=parent.get('revision',0)+1:errors.append('revision:must-increment-by-one')
 pref=current.get('parent')
 if not isinstance(pref,dict):errors.append('current.parent:missing')
 else:
  if pref.get('policy_id')!=parent.get('policy_id'):errors.append('current.parent.policy_id:mismatch')
  if pref.get('digest')!=pd:errors.append('current.parent.digest:mismatch')
 source_changed=parent.get('source')!=current.get('source')
 semantic_fields=['goal']
 semantic_changed=[k for k in semantic_fields if parent.get(k)!=current.get(k)]
 policy_fields=['regime','belief','observations','actions','policy','potential','safety_shield','horizon','terminal_states','invalidators','challenge','handoff']
 policy_changed=[k for k in policy_fields if parent.get(k)!=current.get(k)]
 deltas={
  'obligations':delta(rows(parent.get('goal',{}).get('obligations'),'obligation_id'),rows(current.get('goal',{}).get('obligations'),'obligation_id')),
  'facts':delta(rows(parent.get('belief',{}).get('facts'),'fact_id'),rows(current.get('belief',{}).get('facts'),'fact_id')),
  'unknowns':delta(rows(parent.get('belief',{}).get('unknowns'),'unknown_id'),rows(current.get('belief',{}).get('unknowns'),'unknown_id')),
  'observations':delta(rows(parent.get('observations'),'observation_id'),rows(current.get('observations'),'observation_id')),
  'actions':delta(rows(parent.get('actions'),'action_id'),rows(current.get('actions'),'action_id')),
  'rules':delta(rows(parent.get('policy',{}).get('rules'),'rule_id'),rows(current.get('policy',{}).get('rules'),'rule_id')),
  'shield_rules':delta(rows(parent.get('safety_shield',{}).get('rules'),'shield_id'),rows(current.get('safety_shield',{}).get('rules'),'shield_id')),
 }
 summary=current.get('revision_summary',{})
 if semantic_changed and not summary.get('semantic_changes'):warnings.append('revision_summary:missing-semantic-changes')
 if policy_changed and not summary.get('policy_changes'):warnings.append('revision_summary:missing-policy-changes')
 if source_changed and not summary.get('source_changes'):warnings.append('revision_summary:missing-source-changes')
 if a.strict and any(x.startswith('revision_summary:') for x in warnings):errors.append('revision_summary:strict-mismatch')
 if semantic_changed and current.get('source',{}).get('mode')=='spec_handoff' and current.get('gate',{}).get('semantic_drift')!='authorized':errors.append('semantic-change-in-spec-handoff-without-authorization')
 return emit('policy_revision_diff',{'policy_id':current.get('policy_id'),'parent_revision':parent.get('revision'),'current_revision':current.get('revision'),'parent_digest':pd,'current_digest':cd,'source_changed':source_changed,'semantic_changed':semantic_changed,'policy_changed':policy_changed,'deltas':deltas},errors,warnings)
if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env python3
import json, statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/'statewide-master.json'
OPS=ROOT/'operator-crossref.json'
OBS=ROOT/'ap-observations.json'
PROFILES=ROOT/'operator-profiles.json'

master=json.loads(MASTER.read_text(encoding='utf-8'))
rows=master['establishments']
ops=json.loads(OPS.read_text(encoding='utf-8'))
obs=json.loads(OBS.read_text(encoding='utf-8'))
by_license={str(r.get('license') or ''):r for r in rows}

# Rebuild derived scouting/operator fields deterministically. This prevents stale
# values from surviving when an observation or operator cross-reference changes.
derived_fields=(
    'terminal_operator','scout_status','scout_basis','scout_fingerprints',
    'scout_priority_score','scout_priority_band','observation_label',
    'observation_category','observation_notes','observation_tags',
    'observation_current_sets','observation_legacy_sets',
    'ap_status','ap_category','ap_observed_sets'
)
for r in rows:
    for k in derived_fields:
        r.pop(k,None)

# Normalize terminal operator from cross-reference.
for lic,meta in ops.items():
    op=meta.get('operator') if isinstance(meta,dict) else meta
    r=by_license.get(str(lic))
    if r and op:
        r['terminal_operator']=op

profile_seed=defaultdict(lambda:{
    'confirmed_current_locations':0,
    'legacy_locations':0,
    'likely_locations':0,
    'complete_coverage_locations':0,
    'observed_fingerprints':[],
    'observed_current_vgt_counts':[],
})

# Apply direct field observations first.
for lic,o in obs.items():
    r=by_license.get(str(lic))
    if not r:
        continue
    status=o.get('status')
    cat=o.get('category')
    raw_sets=list(o.get('sets') or [])
    current_sets=list(o.get('current_sets') or ([] if cat=='legacy' else raw_sets))
    legacy_sets=list(o.get('legacy_sets') or (raw_sets if cat=='legacy' else []))
    sets=[]
    for fp in current_sets+legacy_sets:
        if fp not in sets: sets.append(fp)
    if status=='likely':
        scout='likely'
    elif status=='confirmed' and cat=='legacy':
        scout='confirmed-legacy'
    else:
        # mixed contains a current AP set plus a legacy set, so it is current-relevant.
        scout='confirmed-current'
    r['scout_status']=scout
    r['scout_basis']='Field observation'
    r['scout_fingerprints']=sets
    # Direct-observation display metadata comes from ap-observations.json so the
    # UI has one source of truth instead of a second hard-coded AP table.
    r['observation_label']=o.get('label') or ('🕰 Old AP Set' if scout=='confirmed-legacy' else '🎰 Confirmed AP Set')
    r['observation_category']=cat or ''
    r['observation_notes']=o.get('notes') or 'Field-confirmed AP games only; unlisted games are not treated as AP.'
    r['observation_tags']=list(o.get('tags') or [])
    r['observation_current_sets']=current_sets
    r['observation_legacy_sets']=legacy_sets
    r['scout_priority_score']=None
    r['scout_priority_band']='observed'

    op=r.get('terminal_operator')
    if not op:
        continue
    p=profile_seed[op]
    if scout=='confirmed-current':
        p['confirmed_current_locations']+=1
        if r.get('vgts') is not None:
            p['observed_current_vgt_counts'].append(int(r['vgts']))
    elif scout=='confirmed-legacy':
        p['legacy_locations']+=1
    elif scout=='likely':
        p['likely_locations']+=1
    if o.get('coverage')=='complete':
        p['complete_coverage_locations']+=1
    # Only confirmed observations seed operator fingerprints. A likely/recollection set
    # remains visible at its own location but is not propagated to other establishments.
    if status=='confirmed':
        # Only current sets seed predictions. Old/legacy sets remain visible at
        # their observed location but do not become operator scouting leads.
        for fp in current_sets:
            if fp not in p['observed_fingerprints']:
                p['observed_fingerprints'].append(fp)

profiles={}
for op,p in sorted(profile_seed.items()):
    vgts=p['observed_current_vgt_counts']
    counts=Counter(vgts)
    typical=[]
    if counts:
        mx=max(counts.values())
        typical=sorted(k for k,v in counts.items() if v==mx)
    # Keep evidence strength descriptive, not a claim about actual game presence.
    strength=min(100, 30 + p['confirmed_current_locations']*12 + p['complete_coverage_locations']*8 + min(12,len(p['observed_fingerprints'])*2))
    profiles[op]={
        **p,
        'typical_vgt_counts':typical,
        'evidence_strength':strength,
        'model_note':'Operator/VGT similarity is a scouting lead only; exact games require field confirmation.'
    }

# Build operator-based leads for unobserved records.
for r in rows:
    if r.get('scout_status') in {'confirmed-current','confirmed-legacy','likely'}:
        continue
    op=r.get('terminal_operator')
    p=profiles.get(op)
    if not p or p['confirmed_current_locations']<=0:
        r['scout_status']='unknown'
        r['scout_basis']='No field-confirmed AP observation or operator fingerprint available'
        r['scout_fingerprints']=[]
        r['scout_priority_score']=0
        r['scout_priority_band']='none'
        continue

    score=45 + min(15,p['confirmed_current_locations']*3) + min(6,p['complete_coverage_locations']*3)
    vgt_note='VGT count unavailable'
    v=r.get('vgts')
    typical=p.get('typical_vgt_counts') or []
    if v is not None and typical:
        delta=min(abs(int(v)-int(t)) for t in typical)
        if delta==0:
            score+=12; vgt_note=f"VGT count {v} exactly matches the operator's most common observed AP-location count"
        elif delta==1:
            score+=6; vgt_note=f"VGT count {v} is within 1 of the operator's most common observed AP-location count"
        else:
            vgt_note=f"VGT count {v} differs from the operator's most common observed AP-location count(s)"
    score=max(0,min(85,int(score)))
    band='high' if score>=68 else ('medium' if score>=58 else 'low')
    r['scout_status']='operator-lead'
    r['scout_priority_score']=score
    r['scout_priority_band']=band
    r['scout_basis']=(f"Same terminal operator as {p['confirmed_current_locations']} field-confirmed current AP location(s); {vgt_note}")
    r['scout_fingerprints']=p['observed_fingerprints']

PROFILES.write_text(json.dumps(profiles,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
master['metadata']=master.get('metadata') or {}
master['metadata']['scouting_model_version']='13.3.3'
master['metadata']['scouting_model_note']='Priority ranks unvisited scouting targets by operator evidence and VGT-count similarity; it does not predict gambling outcomes or confirm exact games.'
MASTER.write_text(json.dumps(master,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

bands=Counter(r.get('scout_priority_band') for r in rows)
statuses=Counter(r.get('scout_status') for r in rows)
print(json.dumps({'statuses':statuses,'priority_bands':bands,'operator_profiles':len(profiles)},indent=2,default=dict))

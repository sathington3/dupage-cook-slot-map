#!/usr/bin/env python3
import json,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; MASTER=ROOT/'statewide-master.json'; EST=ROOT/'establishments.js'; QUEUE=ROOT/'enrichment-queue.csv'
def c(v):return str(v or '').strip()
m=json.loads(MASTER.read_text());live=[]
for r in m['establishments']:
    if r.get('lat') in (None,'') or r.get('lon') in (None,''):continue
    # Keep the live bundle lean: revenue source details and null/empty AP fields remain in statewide-master.json.
    keys=('county','name','address','city','state','zip','license','type','lat','lon','vgts','played','payback')
    d={k:r.get(k) for k in keys}
    # License is the permanent IGB key. UI/local-state IDs must not depend on
    # county ordering or an old imported row number.
    canonical_id=f"IL-{c(r.get('license'))}"
    legacy_id=c(r.get('id'))
    d['id']=canonical_id
    if legacy_id and legacy_id!=canonical_id: d['_legacy_id']=legacy_id
    for k in ('terminal_operator','scout_status','scout_basis','scout_fingerprints','scout_priority_score','scout_priority_band','observation_label','observation_category','observation_notes','observation_tags','observation_current_sets','observation_legacy_sets'):
        v=r.get(k)
        if v not in (None,'',[],{},'unknown','none',0): d[k]=v
    # Unknown is the frontend default, so omitting it saves substantial payload size.
    d['_public_search']=' '.join(c(d.get(k)).lower() for k in ('name','address','city','state','zip','license','county') if c(d.get(k)))
    op=c(d.get('terminal_operator')).lower()
    if op: d['_search']=d['_public_search']+' '+op
    live.append(d)
EST.write_text('/* Slot Map establishment data. Generated from statewide-master.json; verified coordinates only. */\nconst R='+json.dumps(live,separators=(',',':'),ensure_ascii=False)+';\n')
fields=['license','name','municipality','county','county_source','address','city','zip','lat','lon','status'];rows=[]
for r in m['establishments']:
    if r.get('record_status')!='current_igb' or (r.get('lat') not in (None,'') and r.get('lon') not in (None,'')):continue
    rows.append({'license':c(r.get('license')),'name':c(r.get('name')),'municipality':c(r.get('municipality')),'county':c(r.get('county')),'county_source':c(r.get('county_source')),'address':c(r.get('address')),'city':c(r.get('city')),'zip':c(r.get('zip')),'lat':'','lon':'','status':'needs_coordinates' if c(r.get('address')) else 'needs_address_and_coordinates'})
with QUEUE.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print(json.dumps({'mapped_records':len(live),'remaining_queue':len(rows)},indent=2))

#!/usr/bin/env python3
import json,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; MASTER=ROOT/'statewide-master.json'; EST=ROOT/'establishments.js'; QUEUE=ROOT/'enrichment-queue.csv'
def c(v):return str(v or '').strip()
m=json.loads(MASTER.read_text());live=[]
for r in m['establishments']:
    if r.get('lat') in (None,'') or r.get('lon') in (None,''):continue
    keys=('county','id','name','address','city','state','zip','license','type','lat','lon','vgts','played','won','nti','payback','terminal_operator','ap_status','ap_category')
    d={k:r.get(k) for k in keys}; d['id']=d.get('id') or f"IL-{c(r.get('license'))}"; d['_search']=' '.join(c(d.get(k)).lower() for k in ('name','address','city','state','zip','license','county','terminal_operator') if c(d.get(k)));live.append(d)
EST.write_text('/* Slot Map establishment data. Generated from statewide-master.json; verified coordinates only. */\nconst R='+json.dumps(live,separators=(',',':'),ensure_ascii=False)+';\n')
fields=['license','name','municipality','county','county_source','address','city','zip','lat','lon','status'];rows=[]
for r in m['establishments']:
    if r.get('record_status')!='current_igb' or (r.get('lat') not in (None,'') and r.get('lon') not in (None,'')):continue
    rows.append({'license':c(r.get('license')),'name':c(r.get('name')),'municipality':c(r.get('municipality')),'county':c(r.get('county')),'county_source':c(r.get('county_source')),'address':c(r.get('address')),'city':c(r.get('city')),'zip':c(r.get('zip')),'lat':'','lon':'','status':'needs_coordinates' if c(r.get('address')) else 'needs_address_and_coordinates'})
with QUEUE.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print(json.dumps({'mapped_records':len(live),'remaining_queue':len(rows)},indent=2))

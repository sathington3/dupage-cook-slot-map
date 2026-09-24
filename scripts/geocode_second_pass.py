#!/usr/bin/env python3
"""Second-pass Census geocoder for unresolved Slot Map addresses.

Only promotes Census Match + Exact results. It retries conservative address
variants (removing PO-box prefixes and unit/suite suffixes) to turn formatting
problems into exact street-address matches without accepting fuzzy coordinates.
"""
from __future__ import annotations
import argparse,csv,io,json,re,time,urllib.request,urllib.error,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/'statewide-master.json'; CACHE=ROOT/'geocoding-second-pass-cache.json'; RESULTS=ROOT/'geocoding-second-pass-results.csv'
CENSUS='https://geocoding.geo.census.gov/geocoder/locations/addressbatch'; BENCH='Public_AR_Current'; IL=(36.8,42.55,-91.6,-87.35)
def c(v): return str(v or '').strip()
def street_number(a):
    m=re.match(r'\s*(\d+)',c(a)); return m.group(1) if m else None
def suspicious_collision(master,candidate,lat,lon):
    n=street_number(candidate.get('address'))
    if not n:return None
    key=(round(float(lat),7),round(float(lon),7))
    for other in master['establishments']:
        if other is candidate or other.get('lat') in (None,'') or other.get('lon') in (None,''):continue
        if (round(float(other['lat']),7),round(float(other['lon']),7))!=key:continue
        on=street_number(other.get('address'))
        if on and on!=n:return other
    return None
def inside(lat,lon): return IL[0]<=lat<=IL[1] and IL[2]<=lon<=IL[3]
def simplify(a):
    s=c(a)
    s=re.sub(r'(?i)^\s*(?:P\.?\s*O\.?\s*BOX|POST OFFICE BOX)\s+[^,]+,?\s*','',s)
    s=re.sub(r'(?i),?\s+(?:SUITE|STE|UNIT|BLDG|BUILDING|FLOOR|FL|#)\s*[A-Z0-9-]+.*$','',s).strip(' ,')
    # If address contains a PO box followed by a street address, keep the street portion.
    m=re.search(r'(?i)(\d+[A-Z-]*\s+.+)$',s)
    return m.group(1).strip() if m else s
def multipart(data,b):
    out=bytearray(); cr=b'\r\n'
    def add(x): out.extend(x)
    add(f'--{b}'.encode());add(cr);add(b'Content-Disposition: form-data; name="benchmark"');add(cr);add(cr);add(BENCH.encode());add(cr)
    add(f'--{b}'.encode());add(cr);add(b'Content-Disposition: form-data; name="addressFile"; filename="addresses.csv"');add(cr);add(b'Content-Type: text/csv');add(cr);add(cr);add(data);add(cr);add(f'--{b}--'.encode());add(cr);return bytes(out)
def call(rows,retries=6):
    s=io.StringIO(newline=''); w=csv.writer(s,lineterminator='\n')
    for r in rows:w.writerow([r['license'],r['variant'],r['city'],'IL',r['zip']])
    b='----SlotMapSecondPass'; body=multipart(s.getvalue().encode(),b); last=None
    for i in range(retries):
        req=urllib.request.Request(CENSUS,data=body,headers={'Content-Type':f'multipart/form-data; boundary={b}','User-Agent':'SlotMap/13.4.0-second-pass'},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=120) as resp:return list(csv.reader(io.StringIO(resp.read().decode('utf-8-sig',errors='replace'))))
        except Exception as e:
            last=e; time.sleep(min(60,3*(2**i)))
    raise RuntimeError(last)
def parse(row):
    x=list(row)+['']*8; lic,status,typ,addr,coord=c(x[0]),c(x[2]),c(x[3]),c(x[4]),c(x[5]); lat=lon=None
    if coord and ',' in coord:
        try: lon,lat=map(float,[z.strip() for z in coord.split(',')[:2]])
        except: pass
    ok=status.casefold()=='match' and typ.casefold()=='exact' and lat is not None and inside(lat,lon)
    return {'license':lic,'status':status,'match_type':typ,'matched_address':addr,'lat':lat,'lon':lon,'accepted':ok,'reason':'second_pass_exact' if ok else ('second_pass_non_exact' if status.casefold()=='match' else 'second_pass_no_match')}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--batch-size',type=int,default=200);ap.add_argument('--limit',type=int,default=0);ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
    m=json.loads(MASTER.read_text()); cache=json.loads(CACHE.read_text()) if CACHE.exists() else {}
    pending=[]
    for r in m['establishments']:
        if r.get('record_status')!='current_igb' or r.get('lat') not in (None,'') or not c(r.get('address')):continue
        lic=c(r.get('license')); v=simplify(r.get('address'))
        if not v or v.casefold()==c(r.get('address')).casefold() or lic in cache:continue
        pending.append({'license':lic,'variant':v,'city':c(r.get('city') or r.get('municipality')),'zip':c(r.get('zip'))[:5]})
    if args.limit: pending=pending[:args.limit]
    print(f'Second-pass candidates: {len(pending)}')
    if args.dry_run:return
    for i in range(0,len(pending),args.batch_size):
        chunk=pending[i:i+args.batch_size]
        try: out=call(chunk)
        except Exception as e: print('WARNING batch failed',e);continue
        for row in out:
            q=parse(row); cache[q['license']]=q
        CACHE.write_text(json.dumps(cache,indent=2,sort_keys=True)); print(f'Processed {min(i+len(chunk),len(pending))}/{len(pending)}',flush=True)
    bylic={c(r.get('license')):r for r in m['establishments']}
    added=0
    for lic,q in cache.items():
        r=bylic.get(lic)
        if not r or not q.get('accepted') or r.get('lat') not in (None,''):continue
        # ZIP guardrail from returned matched address when present
        mm=re.search(r'\b(\d{5})(?:-\d{4})?\s*$',c(q.get('matched_address'))); mz=mm.group(1) if mm else ''; ez=c(r.get('zip'))[:5]
        if ez and mz and ez!=mz: q['accepted']=False;q['reason']='second_pass_zip_mismatch';continue
        lat=round(float(q['lat']),7);lon=round(float(q['lon']),7)
        collision=suspicious_collision(m,r,lat,lon)
        if collision:
            q['accepted']=False;q['reason']='coordinate_collision_different_street_number';q['collision_license']=c(collision.get('license'));continue
        r['lat']=lat;r['lon']=lon;r['mapping_status']='mapped_census_exact_second_pass';r['coordinate_source']='us_census_batch_geocoder_second_pass';added+=1
    MASTER.write_text(json.dumps(m,indent=2,ensure_ascii=False))
    fields=['license','status','match_type','accepted','reason','collision_license','lat','lon','matched_address']
    with RESULTS.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();[w.writerow({k:v.get(k,'') for k in fields}) for _,v in sorted(cache.items())]
    print(f'Added {added} second-pass exact coordinates. Run scripts/geocode_statewide.py --dry-run afterward to rebuild live files, or use the workflow.')
if __name__=='__main__':main()

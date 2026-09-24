#!/usr/bin/env python3
"""Merge the official IGB Video Gaming *Licensees* CSV into statewide-master.json.

Usage:
  python scripts/import_igb_licensees.py /path/to/IGB-licensees.csv

The monthly revenue file does not contain street addresses. The IGB licensee export does.
This importer is deliberately tolerant of column-name changes and only merges records when
an IGB video-gaming license number matches exactly.

It never invents a county, ZIP, address or coordinate.
"""
from __future__ import annotations
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / 'statewide-master.json'
QUEUE = ROOT / 'enrichment-queue.csv'
OUT_LICENSEES = ROOT / 'igb-licensee-addresses.json'

ESTABLISHMENT_TYPES = {
    'licensed establishment','licensed fraternal establishment','licensed veterans establishment',
    'licensed truck stop establishment','licensed large truck stop establishment',
    'establishment','fraternal establishment','veterans establishment','truck stop establishment',
    'large truck stop establishment'
}

def norm(s):
    return re.sub(r'[^a-z0-9]+','',str(s or '').strip().lower())

def clean(s):
    return str(s or '').strip().strip('\ufeff')

def field(row, *names):
    by={norm(k):v for k,v in row.items() if k is not None}
    for n in names:
        v=by.get(norm(n))
        if v is not None and clean(v): return clean(v)
    return ''

def parse_city_state_zip(row):
    city=field(row,'city','business city','location city')
    state=field(row,'state','business state','location state')
    zipcode=field(row,'zip','zip code','zipcode','postal code','business zip','location zip')
    combined=field(row,'city-state','city state','city/state/zip','city state zip','city-state-zip')
    if combined and (not city or not state or not zipcode):
        # Handles common values like "Springfield, IL 62704".
        m=re.match(r'^\s*(.*?)\s*,?\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\s*$',combined,re.I)
        if m:
            city=city or m.group(1).strip(' ,')
            state=state or m.group(2).upper()
            zipcode=zipcode or m.group(3)
    return city,state,zipcode

def read_rows(path):
    raw=Path(path).read_text(encoding='utf-8-sig',errors='replace').splitlines()
    # Locate the actual header; IGB exports sometimes prepend title/date rows.
    header_idx=None
    for i,line in enumerate(raw[:30]):
        low=line.lower()
        if ('license' in low and ('address' in low or 'business name' in low or 'name' in low)):
            header_idx=i; break
    if header_idx is None: header_idx=0
    return list(csv.DictReader(raw[header_idx:]))

def main():
    if len(sys.argv)!=2:
        raise SystemExit('Usage: python scripts/import_igb_licensees.py /path/to/IGB-licensees.csv')
    rows=read_rows(sys.argv[1])
    licmap={}
    skipped_type=0
    for row in rows:
        lic=field(row,'license number','license no','license #','license','licensenumber')
        if not lic: continue
        ltype=field(row,'license type','type','license category')
        if ltype and norm(ltype) not in {norm(x) for x in ESTABLISHMENT_TYPES}:
            # Some IGB exports have a broad Licensees list containing manufacturers/operators too.
            skipped_type += 1
            continue
        city,state,zipcode=parse_city_state_zip(row)
        rec={
            'license':lic,
            'name':field(row,'business name','legal name','name','licensee name'),
            'dba':field(row,'d/b/a','dba','doing business as','business dba'),
            'address':field(row,'address','street address','business address','location address'),
            'city':city,
            'state':state or 'IL',
            'zip':zipcode,
            'county':field(row,'county','business county','location county'),
            'license_type':ltype,
            'license_status':field(row,'license status','status'),
        }
        licmap[lic]=rec

    master=json.loads(MASTER.read_text(encoding='utf-8'))
    matched=addressed=countied=zipped=0
    for e in master['establishments']:
        src=licmap.get(str(e.get('license') or '').strip())
        if not src: continue
        matched += 1
        if src['address']:
            e['address']=src['address']; addressed += 1
        if src['city']: e['city']=src['city']
        if src['state']: e['state']=src['state']
        if src['zip']:
            e['zip']=src['zip']; zipped += 1
        if src['county']:
            e['county']=src['county'].replace(' County','').strip(); e['county_source']='igb_licensee_list'; countied += 1
        if src['license_type']: e['type']=src['license_type'].replace('Licensed ','').strip()
        if src['license_status']: e['license_status']=src['license_status']
        if e.get('address') and e.get('city'):
            if e.get('lat') not in (None,'') and e.get('lon') not in (None,''):
                e['mapping_status']='mapped_verified'
            else:
                e['mapping_status']='address_known_needs_coordinates'

    current=[e for e in master['establishments'] if e.get('record_status')=='current_igb']
    queue=[e for e in current if e.get('lat') in (None,'') or e.get('lon') in (None,'')]
    master['schema_version']='12.2'
    master['licensee_source_file']=Path(sys.argv[1]).name
    master['counts'].update({
        'licensee_rows_imported':len(licmap),
        'licensee_matches':matched,
        'current_with_address':sum(bool(e.get('address')) for e in current),
        'current_with_county':sum(bool(e.get('county')) for e in current),
        'current_with_coordinates':sum(e.get('lat') not in (None,'') and e.get('lon') not in (None,'') for e in current),
        'coordinate_queue':len(queue),
    })
    MASTER.write_text(json.dumps(master,separators=(',',':'),ensure_ascii=False),encoding='utf-8')
    OUT_LICENSEES.write_text(json.dumps({'count':len(licmap),'records':list(licmap.values())},separators=(',',':'),ensure_ascii=False),encoding='utf-8')
    with QUEUE.open('w',newline='',encoding='utf-8') as f:
        fields=['license','name','municipality','county','county_source','address','city','zip','lat','lon','status']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for e in queue:
            w.writerow({
                'license':e.get('license',''),'name':e.get('name',''),'municipality':e.get('municipality',''),
                'county':e.get('county',''),'county_source':e.get('county_source',''),'address':e.get('address',''),
                'city':e.get('city',''),'zip':e.get('zip',''),'lat':e.get('lat',''),'lon':e.get('lon',''),
                'status':'needs_coordinates' if e.get('address') else 'needs_address_and_coordinates'
            })
    print(json.dumps({
        'input_rows':len(rows),'usable_licensees':len(licmap),'skipped_non_establishment_type':skipped_type,
        'matched_master_records':matched,'addresses_merged':addressed,'counties_merged':countied,'zips_merged':zipped,
        'coordinate_queue':len(queue)
    },indent=2))

if __name__=='__main__': main()

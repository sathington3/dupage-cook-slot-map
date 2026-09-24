#!/usr/bin/env python3
"""Build Slot Map's statewide master and enrichment queue.

Inputs (repo root):
  - establishments.js: verified mapped records used by the app
  - igb-statewide-establishments.json: cleaned current IGB statewide report

Outputs:
  - statewide-master.json: current IGB records merged with mapped metadata, plus legacy mapped records
  - enrichment-queue.csv: current IGB records still missing address/coordinates

License number is the stable join key.
"""
from __future__ import annotations
import csv, json, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_mapped():
    text=(ROOT/'establishments.js').read_text(encoding='utf-8')
    m=re.search(r'const R=(\[.*\]);\s*$', text, re.S)
    if not m:
        raise RuntimeError('Could not parse establishments.js')
    return json.loads(m.group(1))


def clean_license(v):
    return str(v or '').strip()


def county_from_municipality(municipality, city_counties):
    m=(municipality or '').strip()
    if m.endswith(' County') and len(m) > len(' County'):
        return m[:-7], 'igb_county_literal'
    counties=city_counties.get(m.casefold(), set())
    if len(counties)==1:
        return next(iter(counties)), 'verified_city_lookup'
    return None, None


def main():
    mapped=load_mapped()
    statewide=json.loads((ROOT/'igb-statewide-establishments.json').read_text(encoding='utf-8'))
    current=statewide['establishments']

    mapped_by_license={clean_license(r.get('license')):r for r in mapped if clean_license(r.get('license'))}
    city_counties=defaultdict(set)
    for r in mapped:
        city=(r.get('city') or '').strip()
        county=(r.get('county') or '').strip()
        if city and county:
            city_counties[city.casefold()].add(county)

    master=[]
    queue=[]
    current_licenses=set()
    stats=defaultdict(int)

    for e in current:
        lic=clean_license(e.get('license'))
        current_licenses.add(lic)
        base={
            'license': lic,
            'name': e.get('name'),
            'municipality': e.get('municipality'),
            'county': None,
            'city': None,
            'address': None,
            'state': 'IL',
            'zip': None,
            'lat': None,
            'lon': None,
            'type': 'Establishment',
            'vgts': e.get('vgts'),
            'played': e.get('played'),
            'won': e.get('won'),
            'nti': e.get('nti'),
            'payback': e.get('payback'),
            'record_status': 'current_igb',
            'mapping_status': 'unmapped',
            'county_source': None,
        }
        existing=mapped_by_license.get(lic)
        if existing:
            # Keep verified location fields; refresh current IGB gaming/revenue fields.
            for k in ('county','city','address','state','zip','lat','lon','type','id'):
                if existing.get(k) not in (None,''):
                    base[k]=existing.get(k)
            base['mapping_status']='mapped_verified'
            base['county_source']='mapped_dataset'
            stats['mapped_verified']+=1
        else:
            county, source=county_from_municipality(e.get('municipality'), city_counties)
            if county:
                base['county']=county
                base['county_source']=source
                base['mapping_status']='county_known'
                stats[source]+=1
            else:
                stats['county_unresolved']+=1
            queue.append({
                'license': lic,
                'name': e.get('name'),
                'municipality': e.get('municipality'),
                'county': base['county'] or '',
                'county_source': base['county_source'] or '',
                'address': '', 'city': '', 'zip': '', 'lat': '', 'lon': '',
                'status': 'needs_address_and_coordinates'
            })
        master.append(base)

    # Preserve verified mapped locations absent from this current report; mark them legacy.
    for r in mapped:
        lic=clean_license(r.get('license'))
        if lic and lic in current_licenses:
            continue
        rec=dict(r)
        rec.update({
            'municipality': rec.get('city'),
            'record_status':'legacy_mapped_not_in_current_igb',
            'mapping_status':'mapped_verified',
            'county_source':'mapped_dataset',
        })
        master.append(rec)
        stats['legacy_mapped']+=1

    out={
        'schema_version':'12.1',
        'source_report':statewide.get('report'),
        'source_period':statewide.get('period'),
        'source_report_date':statewide.get('report_date'),
        'license_key':'license',
        'counts':{
            'current_igb_unique':len(current),
            'current_mapped_verified':stats['mapped_verified'],
            'current_county_known_not_mapped':stats['igb_county_literal']+stats['verified_city_lookup'],
            'current_county_unresolved_not_mapped':stats['county_unresolved'],
            'legacy_mapped_preserved':stats['legacy_mapped'],
            'master_total':len(master),
            'enrichment_queue':len(queue),
        },
        'establishments':master,
    }
    (ROOT/'statewide-master.json').write_text(json.dumps(out,separators=(',',':'),ensure_ascii=False),encoding='utf-8')
    with (ROOT/'enrichment-queue.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['license','name','municipality','county','county_source','address','city','zip','lat','lon','status']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(queue)
    print(json.dumps(out['counts'],indent=2))

if __name__=='__main__':
    main()

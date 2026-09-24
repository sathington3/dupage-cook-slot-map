#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]
# required files
for name in ['index.html','establishments.js','statewide-master.json','igb-statewide-establishments.json','manifest.webmanifest','service-worker.js','buffalo-theme.png','app-icon-512.png','apple-touch-icon.png']:
    if not (ROOT/name).exists(): errors.append(f'missing {name}')
# mapped JS
text=(ROOT/'establishments.js').read_text(encoding='utf-8')
m=re.search(r'const R=(\[.*\]);\s*$',text,re.S)
if not m: errors.append('establishments.js parse failed'); mapped=[]
else: mapped=json.loads(m.group(1))
licenses=[str(r.get('license') or '') for r in mapped if r.get('license')]
if len(licenses)!=len(set(licenses)): errors.append('duplicate mapped license IDs')
# master
master=json.loads((ROOT/'statewide-master.json').read_text(encoding='utf-8'))
rows=master['establishments']; ml=[str(r.get('license') or '') for r in rows if r.get('license')]
if len(ml)!=len(set(ml)): errors.append('duplicate master license IDs')
# coordinates sanity
for r in mapped:
    lat,lon=r.get('lat'),r.get('lon')
    if lat is not None and lon is not None and not (36.8 <= float(lat) <= 42.6 and -91.6 <= float(lon) <= -87.0):
        errors.append(f"coordinate outside IL bounds: {r.get('license')}")
# cache/version
idx=(ROOT/'index.html').read_text(encoding='utf-8')
sw=(ROOT/'service-worker.js').read_text(encoding='utf-8')
EXPECTED_VERSION='12.6'
if f'v={EXPECTED_VERSION}' not in idx: errors.append(f'index asset version not {EXPECTED_VERSION}')
if f'slot-map-v{EXPECTED_VERSION}' not in sw: errors.append(f'service worker cache not {EXPECTED_VERSION}')
print(json.dumps({'mapped_records':len(mapped),'master_records':len(rows),'errors':errors},indent=2))
sys.exit(1 if errors else 0)

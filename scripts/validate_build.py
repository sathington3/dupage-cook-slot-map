#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]
# required files
for name in ['index.html','establishments.js','statewide-master.json','igb-statewide-establishments.json','manifest.webmanifest','service-worker.js','buffalo-theme.png','app-icon-512.png','apple-touch-icon.png','operator-crossref.json','operator-profiles.json','ap-observations.json']:
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

# Stable live IDs must be based on the permanent IGB license key.
for r in mapped:
    lic=str(r.get('license') or '').strip()
    if lic and r.get('id')!=f'IL-{lic}': errors.append(f"noncanonical live id for {lic}: {r.get('id')}")

# Census exact matches must never reuse an exact coordinate for a different
# leading street number. Same-address/suite businesses are intentionally allowed.
def street_number(a):
    m=re.match(r'\s*(\d+)',str(a or ''));return m.group(1) if m else None
coord_groups={}
for r in rows:
    if r.get('lat') in (None,'') or r.get('lon') in (None,''): continue
    coord_groups.setdefault((round(float(r['lat']),7),round(float(r['lon']),7)),[]).append(r)
for coord,group in coord_groups.items():
    census=[r for r in group if str(r.get('coordinate_source') or '').startswith('us_census_')]
    if not census: continue
    nums={street_number(r.get('address')) for r in group if street_number(r.get('address'))}
    if len(nums)>1: errors.append(f'suspicious Census coordinate collision at {coord}: {[str(r.get("license")) for r in group]}')
# cache/version
idx=(ROOT/'index.html').read_text(encoding='utf-8')
sw=(ROOT/'service-worker.js').read_text(encoding='utf-8')
EXPECTED_VERSION='13.4.0'
for asset in ['manifest.webmanifest','establishments.js','service-worker.js']:
    if f"{asset}?v={EXPECTED_VERSION}" not in idx: errors.append(f'{asset} reference not {EXPECTED_VERSION}')
if f"slot-map-v{EXPECTED_VERSION}" not in sw: errors.append(f'service worker cache not {EXPECTED_VERSION}')
# display-name hygiene
for fld in ['city','county']:
    bad=[r.get(fld) for r in rows if isinstance(r.get(fld),str) and len(r.get(fld).strip())>2 and r.get(fld).strip().isupper()]
    if bad: errors.append(f'all-caps {fld} names remain: {len(bad)}')
# operator/AP metadata sanity
opx=ROOT/'operator-crossref.json'; apx=ROOT/'ap-observations.json'
# operator cross-reference consistency
op=json.loads(opx.read_text(encoding='utf-8')) if opx.exists() else {}
row_by_license={str(r.get('license') or ''):r for r in rows}
for lic,name in op.items():
    if isinstance(name,dict): name=name.get('operator')
    hit=row_by_license.get(str(lic))
    if hit and name and hit.get('terminal_operator')!=name: errors.append(f'operator mismatch for {lic}')
if not opx.exists(): errors.append('missing operator-crossref.json')
if not apx.exists(): errors.append('missing ap-observations.json')

# scouting model sanity
profiles=json.loads((ROOT/'operator-profiles.json').read_text(encoding='utf-8'))
valid={'confirmed-current','confirmed-legacy','likely','operator-lead','unknown'}
for r in rows:
    if r.get('scout_status') not in valid: errors.append(f"invalid scout status {r.get('license')}: {r.get('scout_status')}")
for r in mapped:
    if (r.get('scout_status') or 'unknown') not in valid: errors.append(f"invalid mapped scout status {r.get('license')}")

# scouting priority model sanity
for r in rows:
    st=r.get('scout_status')
    band=r.get('scout_priority_band')
    score=r.get('scout_priority_score')
    if st=='operator-lead':
        if band not in {'high','medium','low'}: errors.append(f"invalid scout priority band {r.get('license')}: {band}")
        if not isinstance(score,(int,float)) or not (0 <= score <= 100): errors.append(f"invalid scout priority score {r.get('license')}: {score}")
    elif st in {'confirmed-current','confirmed-legacy','likely'}:
        if band!='observed': errors.append(f"observed record missing observed priority band {r.get('license')}")
    elif st=='unknown' and band!='none':
        errors.append(f"unknown record has unexpected priority band {r.get('license')}: {band}")
for op,p in profiles.items():
    if p.get('confirmed_current_locations',0) < 1: errors.append(f'operator profile without current evidence: {op}')
    if not p.get('observed_fingerprints'): errors.append(f'operator profile without fingerprints: {op}')


# Illinois county canonicalization / public-search sanity
county_names=sorted({str(r.get('county')).strip() for r in rows if r.get('county')})
county_fold={}
for name in county_names:
    county_fold.setdefault(name.casefold(),[]).append(name)
county_dupes={k:v for k,v in county_fold.items() if len(v)>1}
if county_dupes: errors.append(f'duplicate county display variants: {county_dupes}')
if len(county_names)!=102: errors.append(f'expected 102 canonical Illinois counties, found {len(county_names)}')
if '"_public_search"' not in text: errors.append('establishments.js missing _public_search')

# v13.3 field-report + Public/AP mode architecture sanity
for token in ['fieldreportfilter','exportfield','slotmap-field-reports','FIELD_REPORT_LABELS','exportFieldData',"slot_map_export_version:'13.4.0'",'AP_MODE_DEFAULT','AP_MODE_ENABLED','setAPMode','data-ap-only','body:not(.ap-mode)','LIST_PAGE_SIZE','appendMoreResults','option[data-ap-only]']:
    if token not in idx: errors.append(f'missing field-report feature token: {token}')

# v13.4.0 deep-audit efficiency/reliability invariants
est_text=(ROOT/'establishments.js').read_text(encoding='utf-8')
for forbidden in ['\"won\":','\"nti\":','\"ap_status\":','\"ap_category\":']:
    if forbidden in est_text: errors.append(f'live bundle contains redundant field {forbidden}')
for token in ['MARKER_CACHE','CITIES_BY_COUNTY','nearestRecord','render(true)','flushNotes','writeJSON','migrateLegacyStateKeys','_legacy_id','observation_current_sets','scoutDashboard','data-scout-preset','openNextScout','data-report-pick','data-report-all']:
    if token not in idx: errors.append(f'missing deep-audit optimization: {token}')
if "'./establishments.js','./establishments.js?v=" in sw: errors.append('service worker caches duplicate establishments.js variants')
if 'CDN_SHELL' not in sw: errors.append('service worker does not preserve fixed UI libraries for offline boot')

if 'const AP_META=' in idx or 'const LATTNER_LICENSES=' in idx or 'const ACCEL_LICENSES=' in idx:
    errors.append('stale hard-coded AP/operator table remains in index.html')
if 'coordinate_collision_different_street_number' not in (ROOT/'scripts/geocode_statewide.py').read_text(encoding='utf-8') or 'coordinate_collision_different_street_number' not in (ROOT/'scripts/geocode_second_pass.py').read_text(encoding='utf-8'):
    errors.append('geocoder collision guard missing')

print(json.dumps({'mapped_records':len(mapped),'master_records':len(rows),'known_operator_records':sum(1 for r in rows if r.get('terminal_operator')),'ap_observation_records':sum(1 for r in rows if r.get('scout_status') in {'confirmed-current','confirmed-legacy','likely'}),'errors':errors},indent=2))
sys.exit(1 if errors else 0)

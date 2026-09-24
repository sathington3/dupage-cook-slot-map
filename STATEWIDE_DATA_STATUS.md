# Slot Map v12.3 — statewide bulk-geocoding pipeline

## Current verified data
- Statewide master records: 9,437
- Current unique IGB licenses: 9,300
- Existing verified map records: 1,952
- Current records with official IGB street addresses: 8,897
- Current records with county: 8,993
- Current records eligible for bulk geocoding now: 7,223

## New in v12.3
- Added `scripts/geocode_statewide.py`.
- Uses the U.S. Census batch geocoder with no API key.
- Caches results in `geocoding-cache.json` so reruns do not repeat completed lookups.
- Accepts only Census `Match` + `Exact` results inside Illinois bounds.
- Rejects returned ZIP codes that conflict with the official IGB ZIP.
- Rebuilds `establishments.js` from verified-coordinate records only.
- Rebuilds `enrichment-queue.csv` for unresolved locations.
- Added `.github/workflows/geocode-statewide.yml` so the full batch can run in GitHub Actions where outbound network access is available.

## Safety rule
No approximate municipality centroids or guessed coordinates are promoted to the live map. A location is added only after a verified coordinate source passes validation.

## Environment note
The ChatGPT code container used to assemble this release cannot make the required outbound POST to the Census batch endpoint. The geocoding pipeline was dry-run locally against all 7,223 eligible records and syntax/structure validation passed. The included GitHub Actions workflow is the execution path for the live batch request.


## v12.4 resilience update
- Census HTTP 5xx failures no longer abort the statewide run.
- Default workflow batch size reduced to 250.
- Failed batches are recursively split to 25 records before being deferred.
- Transiently failed records remain uncached and retryable on the next run.
- GitHub Actions timeout increased to 180 minutes.


## v12.6 place-name casing cleanup
- Normalized live City and County display names to title case.
- Preserved Illinois-specific casing such as McHenry, DeKalb, LaSalle, Du Quoin, St. Charles, O'Fallon, and La Harpe.
- Future IGB licensee imports now normalize all-uppercase place names before merging.


## v12.7.1 operator + AP foundation / second-pass geocoding
- Formalized 650 prior IGB terminal-operator cross-reference records into `operator-crossref.json` and the statewide master.
- Added a Terminal Operator filter to the app for locations with known operator data.
- Added structured `ap-observations.json`; AP game lists contain only games explicitly identified as AP-relevant.
- Added field-confirmed observations for STATS Sports Bar, Eva's Place, and Mrs. T's Pizza & Pub.
- Added `scripts/geocode_second_pass.py` and a GitHub Action that retries unresolved official addresses using conservative normalized variants.
- The second pass still accepts Census `Match + Exact` only; it does not loosen coordinate quality standards.


## v12.7.1 audit
- Fixed stale manifest/service-worker query versions.
- Batched DOM card insertion and marker-cluster insertion for more efficient statewide rendering.
- Added icon files to the offline shell cache.
- Strengthened validation for version drift, all-caps place names, and operator cross-reference consistency.


## v12.8 second-pass merge
- 4 safe exact Census matches promoted
- 6 suspicious duplicate-coordinate matches quarantined
- 6,611 mapped establishments
- 2,819 establishments remain in enrichment queue

## v13.0 scouting priority workflow
- Added a maintainable `scripts/build_scouting_model.py` step.
- Operator scouting leads now receive a workflow priority from terminal-operator evidence plus VGT-count similarity to field-confirmed current AP locations.
- Added High / Medium / Low scouting-priority bands: 407 high, 160 medium, 72 low across 639 operator leads.
- Added `Sort By: Scouting Priority`, an `Unvisited Scouting Leads` filter, and High / Medium / Low unvisited priority filters.
- Marking an establishment Visited lowers its runtime scouting rank so already-checked locations do not crowd out new targets.
- Likely/recollection observations are not propagated into operator fingerprints; only field-confirmed observations seed predictions for other locations.
- Scouting priority is explicitly a reconnaissance workflow score, not a probability of a game being present and not a gambling-outcome prediction.


## v13.1 scouting worklist

Added a persistent device-local Scout List, Scout List filter, card/popup controls, and a location-aware Scout Route sort. The route sort prioritizes saved stops and scouting evidence, then distance; it does not alter AP confidence or geocoding data.


## v13.2.1 field workflow
- Added local field reports with four outcomes: AP found, old AP found, no AP found, revisit needed.
- Added machine coverage fields (checked / total).
- Added Field Reports filter.
- Added Export Scout Data JSON backup/share workflow.
- Field reports remain local until explicitly exported/reviewed, preventing accidental model contamination.


## v13.3 Public / AP Mode architecture

The application now has a centralized `AP_MODE_ENABLED` boundary. Development defaults AP Mode on, preserving the current workflow. Public Mode suppresses AP/operator scouting controls, observations, scout list/priority tools, field reports, AP-specific popup details, and AP-specific stats, while leaving the general statewide map features available. Sensitive AP data is still bundled during development; it must be moved behind a private/authenticated data layer before public commercial release.


## v13.3.1 audit hardening
- Fixed delayed Public → AP mode unlock so terminal-operator options populate after unlock.
- AP-only sort options are explicitly hidden/disabled in Public Mode for mobile-browser consistency.
- Statewide establishment cards render in 250-row chunks; all filtered map markers still render.
- Added Show More control to expand long lists without creating thousands of DOM cards at once.
- Service-worker/cache version aligned to v13.3.1.

## v13.3.2 deep efficiency audit
- 9,437 statewide master records; 6,611 verified mapped/live records.
- Live establishments.js reduced by ~34% uncompressed with no loss of frontend-used data.
- Marker reuse, indexed dropdowns, one-pass nearest lookup, map-preserving list interactions, guarded/debounced storage, and tighter service-worker caching added.
- Full validator passes with zero errors.

## v13.3.3 final maintenance hardening

- Live/browser identity now uses canonical `IL-<license>` IDs with automatic migration from legacy IDs.
- Direct AP display metadata is generated from `ap-observations.json`; duplicate hard-coded AP tables were removed from the UI.
- Mixed observations can distinguish current vs old AP sets, and only current sets seed operator scouting fingerprints.
- Both Census geocoders now reject exact-coordinate collisions between different leading street numbers.
- Field-report machine counts receive integer/range validation.
- Current totals remain 9,437 master records and 6,611 verified mapped establishments.

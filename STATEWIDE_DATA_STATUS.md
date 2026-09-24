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

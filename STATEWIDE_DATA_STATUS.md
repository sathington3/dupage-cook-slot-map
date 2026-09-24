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

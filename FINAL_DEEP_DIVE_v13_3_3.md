# Slot Map v13.3.3 final deep-dive audit

This pass focused on bugs and changes that reduce future maintenance risk. It intentionally did not refactor working code just for style.

## Fixed now

- **Permanent local-state identity:** live records now use `IL-<IGB license>` as the canonical ID. Existing browser Favorites, Visited, Notes, Scout List, and Field Reports are migrated from legacy row IDs on first load. This prevents a future statewide rebuild from attaching saved data to the wrong establishment.
- **Selected-card pagination bug:** choosing “View establishment” from a map popup now renders the selected establishment even when it falls beyond the first 250 list cards.
- **Single AP observation source of truth:** direct observation labels/notes/tags now come from `ap-observations.json` through the scouting build. The duplicate hard-coded AP table and large hard-coded operator-license sets were removed from `index.html`.
- **Mixed current/old AP support:** observations can now carry separate current and old-AP sets. Eva’s mixed observation is represented that way, and only current sets seed operator predictions.
- **Deterministic scouting rebuild:** `build_scouting_model.py` clears derived scouting/operator fields before rebuilding them, preventing stale data from surviving a changed source file.
- **Census coordinate-collision guard:** both geocoders now reject an exact Census coordinate if it is already used by a different leading street number. Same-address/suite businesses remain allowed. The validator enforces this for Census-sourced coordinates.
- **Field-report integrity:** machine counts must be non-negative whole numbers, and “machines checked” cannot exceed “machines total.”
- **Service-worker cleanup:** removed one redundant cached root-page entry; the versioned offline shell remains intact.
- **Rebuild documentation:** README now records the source-of-truth files, safe rebuild order, canonical identity rule, validation commands, and the AP-data security caveat.

## Deliberately not changed

- The monolithic static app was not split into a framework/build system. At the current size this would add deployment complexity without a clear user benefit.
- `establishments.js` was not converted to async JSON loading. The current lean bundle is ~3.5 MB and the existing static load path is simple/reliable; this can be revisited if measured mobile startup becomes a problem.
- Map-marker filtering was not rewritten to a complex incremental diff engine. Marker objects are already cached and local-only state changes preserve the map; further complexity is not justified without measured lag.
- OpenStreetMap tiles and unpkg Leaflet/MarkerCluster remain external runtime dependencies. Before a commercial/public launch, use a production tile provider and preferably self-host/vendor the fixed UI libraries.
- AP data is still physically bundled in this development build. Public Mode/Easter-egg hiding is not security. Before broad public release, remove sensitive AP/operator data from the public bundle and load it only from a private authenticated source.

## Validation results

- 9,437 statewide master establishments
- 6,611 verified mapped establishments
- 650 operator-linked establishments
- 12 direct AP observations
- 102 canonical Illinois counties
- 6,611 / 6,611 live IDs are canonical `IL-<license>` IDs
- 0 duplicate live license IDs
- 0 duplicate master license IDs
- 0 validator errors
- JavaScript syntax passed
- service-worker syntax passed
- Python scripts compiled
- geocoder dry-runs passed
- local-state migration test passed
- Census collision-guard synthetic test passed


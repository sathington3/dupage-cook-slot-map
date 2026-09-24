# Slot Map v13.3.3 — Deep Bug / Efficiency Audit

This pass focused on correctness, maintainability, browser performance, storage reliability, and PWA behavior without changing the underlying statewide/AP data model.

## Fixes and optimizations
- Cached Leaflet marker objects instead of recreating thousands of markers on every render.
- Avoided rebuilding the map layer for list-only actions such as Show More, opening/canceling field reports, and local-state changes that do not alter map membership.
- Precomputed county/city/operator lookup lists instead of rescanning all establishments for every dropdown refresh.
- Replaced sort-based nearest-location lookup with a single-pass nearest search.
- Removed per-render object cloning from filtered rows.
- Debounced Notes persistence and added pagehide flushing; localStorage writes now fail gracefully instead of throwing into the UI.
- Reduced repeated stats passes over the filtered array.
- Removed dead/stale AP popup logic and duplicate truck-stop operator metadata; truck-stop display now uses the same terminal-operator/scouting fields as the master model.
- Slimmed establishments.js by removing frontend-unused revenue/AP fields and omitting default/empty scouting values. The live JS payload dropped from about 5.0 MB to about 3.4 MB (~34% smaller uncompressed).
- Removed duplicate service-worker caching of both versioned and unversioned establishments.js.
- Added best-effort caching of the fixed Leaflet/MarkerCluster CDN assets needed for the UI to boot offline, while continuing to leave OpenStreetMap tiles uncached.
- Bumped cache/assets/export version to 13.3.3 and strengthened the build validator for these invariants.

## Data checks
- Master records: 9,437
- Mapped/live records: 6,611
- Canonical Illinois counties: 102
- Duplicate license IDs: 0
- Normalized city/county display variant groups: 0
- Normalized name + address + city duplicate groups: 0
- Live/master record identity fields verified for every mapped record.

## Validation
- JavaScript syntax: passed
- Service worker syntax: passed
- Python scripts: compile cleanly
- validate_build.py: 0 errors
- ZIP integrity: checked after packaging

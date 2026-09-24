# Slot Map v13.3 — Public / AP Mode Architecture

Slot Map now has a centralized feature-mode boundary.

## Development behavior

`AP_MODE_DEFAULT` is currently `true`, so development looks and behaves like the prior build.

## Public Mode

Calling `SlotMapMode.setAPMode(false)` switches the UI to Public Mode. In Public Mode:

- AP scouting filters are hidden and ignored.
- terminal-operator scouting controls are hidden and ignored.
- AP/Old AP observations and operator-lead badges are hidden.
- scout-list controls, scout-priority/route sorts, field reports, and scout export are hidden.
- popups omit AP/operator scouting details and field-report summaries.
- public map features remain: search, county/city, machine count, historical payback, favorites, visited, notes, distance/radius, maps, and establishment details.

Switching modes clears AP-only filter state so a hidden AP filter cannot accidentally affect Public Mode results.

## Important security boundary

v13.3 is an architecture refactor, not secrecy/security. AP data is still bundled in the static app files during development. A future commercial/public release should default Public Mode on and load sensitive AP/operator data only after a private/authenticated unlock, rather than shipping that data in the public bundle.


## v13.3.1 audit hardening
- Fixed delayed Public → AP mode unlock so terminal-operator options populate after unlock.
- AP-only sort options are explicitly hidden/disabled in Public Mode for mobile-browser consistency.
- Statewide establishment cards render in 250-row chunks; all filtered map markers still render.
- Added Show More control to expand long lists without creating thousands of DOM cards at once.
- Service-worker/cache version aligned to v13.3.1.

## v13.3.3 deep-audit hardening
- Marker objects and place/operator indexes are cached to reduce statewide rerender cost.
- Local-only UI changes avoid rebuilding the map cluster layer when map membership is unchanged.
- Notes/storage writes are debounced and guarded.
- The live bundle omits redundant/default fields while statewide-master.json remains the full source of truth.
- Fixed-version Leaflet/MarkerCluster assets are cached best-effort for offline UI boot; map tiles remain online-only.

## v13.3.3 maintenance hardening

- Browser-local state is keyed by canonical `IL-<license>` identity, with automatic migration from legacy row IDs.
- Direct AP observation UI metadata is generated from `ap-observations.json`; there is no duplicate hard-coded AP table in `index.html`.
- Current and old-AP sets can be represented separately at a mixed observation.
- Public/AP separation remains architectural only; sensitive data must leave the public bundle before release.

# Slot Map v13.5.0 update notes

## Implemented

- Establishments sort defaults to **Nearest me**; A–Z remains available.
- Map upper-left mobile control is now an icon-only **Find Me** button that recenters the map without changing filters.
- Added **Open Now** filter support and Open/Closed/Hours unknown status rendering.
- Business hours use `America/Chicago`, support overnight ranges, and keep unknown hours distinct from closed.
- Added `hours_source` and `hours_verified` support to establishment records.
- Preserved Favorites, Visited, Notes, Scout List, and Field Reports via the existing stable IGB-license IDs.
- Added/updated public-facing Oakbrook Terrace names from the city's official gaming-location list while retaining legal names internally.
- Updated field scouting for Johnny's Blitz, Walsh's, and Sabrina's.

## Important hours-data limitation

There is no statewide official IGB feed of operating hours. The UI and data model are ready statewide, but only independently verified hours should be stored. Unknown hours are displayed as **Hours unknown** and are excluded when **Open Now** is enabled. This avoids presenting guessed hours as fact.

At this build, Sabrina's Oakbrook Terrace hours are populated from a current business listing; statewide hours enrichment remains incomplete and should be expanded from reliable sources.

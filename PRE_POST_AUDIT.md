# Slot Map v13.3.1 Pre-Post Audit

This build was re-audited before GitHub deployment.

## Fixes made
- Fixed Public -> AP delayed unlock so the terminal-operator dropdown populates after an unlock.
- Explicitly hides/disables AP-only sort options in Public Mode for mobile browser consistency.
- Added a public-safe search field so operator metadata does not affect Public Mode search results.
- Canonicalized county display variants: `Dupage` -> `DuPage` and `Mcdonough` -> `McDonough`.
- Updated import logic so those county variants are not reintroduced by future IGB imports.
- Added validator enforcement for all 102 canonical Illinois counties.
- Reduced statewide DOM load by rendering establishment cards in 250-row chunks with a Show More control.
- Map markers still represent every filtered mapped establishment.
- Popup HTML is now generated lazily when a marker popup is opened rather than for every marker at initial render.
- Removed an unused stale `snippet.txt` containing older app code.
- Aligned PWA/service-worker cache versioning to v13.3.1.

## Validation
- 9,437 statewide master records
- 6,611 mapped records
- 650 operator-linked records
- 12 AP observation records
- 102 canonical Illinois county names
- 0 duplicate license IDs
- 0 mapped coordinates outside Illinois bounds
- 0 all-caps city/county display names
- JavaScript syntax check passed
- Python scripts compile
- build validator passed with 0 errors

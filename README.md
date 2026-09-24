# Slot Map

Illinois licensed video-gaming establishment map and scouting workspace.

Current build: **v13.4.0**.

## Important development note

The Public/AP feature boundary is architectural during development. AP/operator data is still physically present in this build, so **do not treat Public Mode or a future Easter egg as security**. If this repository or GitHub Pages site is public, the bundled AP data is technically inspectable. Before a wider/public commercial release, move sensitive AP/operator data to a private authenticated source and ship a public bundle that does not contain it.

## Source of truth

- `statewide-master.json` — statewide master keyed by IGB license number.
- `operator-crossref.json` — establishment → terminal-operator links.
- `ap-observations.json` — direct AP field observations. Do not duplicate these observations in `index.html`.
- `scripts/build_scouting_model.py` — derives scouting/operator profiles from the sources above.
- `scripts/rebuild_live.py` — creates the lean, verified-coordinate `establishments.js` used by the app.

The permanent identity key is the **IGB license number**. v13.4.0 migrates older browser-local Favorites/Visited/Notes/Scout List/Field Reports from legacy row IDs to canonical `IL-<license>` IDs. Keep `_legacy_id` aliases in the live build until existing devices have had a reasonable chance to migrate.

## Safe rebuild order

When operator/AP data changes:

```bash
python scripts/build_scouting_model.py
python scripts/rebuild_live.py
python scripts/validate_build.py
```

When geocoding changes, use the GitHub Actions workflows or the geocoding scripts. Both geocoders accept only exact Illinois matches, enforce ZIP checks when available, and reject suspicious exact-coordinate collisions between different street numbers.

## Pre-publish check

Run:

```bash
python scripts/validate_build.py
python -m py_compile scripts/*.py
node --check service-worker.js
```

`validate_build.py` also checks version alignment, canonical IDs, Illinois coordinate bounds, duplicate licenses, county canonicalization, scouting-model integrity, and the Census collision guard.


## v13.4.0 scouting workflow
Adds a Scout Dashboard with practical field presets and a faster, deliberate Field Report entry flow. The prediction model is unchanged.

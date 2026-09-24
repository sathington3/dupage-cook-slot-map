# Slot Map scouting model — v13.1

The scouting layer is designed to answer one narrow question: **which unvisited establishments are more useful to check next for machine-package reconnaissance?** It does not predict wins, payouts, RTP, or that a specific game is present.

## Evidence levels

- **Confirmed Current AP** — field-observed current AP games supplied by the user.
- **Old AP** — field-observed games the user classifies as old AP.
- **Recollection / Likely** — a remembered set that is not currently re-verified.
- **Operator Scouting Lead** — no game is confirmed at this establishment; it shares a terminal operator with field-confirmed current AP locations.
- **Unknown** — no direct observation or usable operator fingerprint is available.

Only games explicitly identified by the user as AP-relevant are stored in the fingerprints. Other games visible in photos are ignored unless the user explicitly adds them.

## Scouting priority

Operator leads receive a conservative scouting-priority score based on:

1. the number of field-confirmed current AP locations linked to that same terminal operator;
2. whether any of those observations had complete establishment coverage; and
3. whether the candidate's VGT count matches (or is within one machine of) the operator's most common VGT count among confirmed current AP locations.

Bands are:

- **High**: score 68+
- **Medium**: score 58–67
- **Low**: below 58

The app's **Sort By: Scouting Priority** puts unvisited likely/recollection targets first, then unvisited operator leads by score. Already field-observed locations are intentionally pushed down because they are not new scouting targets. Marking a location Visited lowers its runtime scouting rank.

The score is a workflow priority only. **It is not a probability that an AP game is present and is not a gambling-outcome score.** Exact game presence always requires field confirmation.


## v13.1 field scouting worklist

- `Scout List` is a local-device worklist saved in browser storage; it does not change the statewide evidence model.
- Establishment cards and map popups can add/remove a location from the Scout List.
- `My Scout List` filters to saved stops.
- `Sort By: Scout Route` requests location and orders saved stops first, then by scouting priority and distance. This is a practical field ordering, not turn-by-turn route optimization.
- Visited status remains independent so a stop can stay on the list until the user removes it.


## v13.2.1 field reports
The app now supports device-local field reports for a visited establishment. Results can be AP Found, Old AP Found, No AP Found, or Revisit Needed. A report can also record only the AP games the scout cares about plus machines checked/total. Saving a report marks the establishment visited. Field reports are stored in browser localStorage and are not silently promoted into the statewide scouting model. Use **Export Scout Data** to create a JSON backup/share file; reviewed observations can then be incorporated deliberately into `ap-observations.json`.


## v13.3 mode boundary

All scouting UI and filters are now gated by the centralized AP Mode flag. Public Mode ignores AP-only filter state as well as hiding the controls, so stale hidden selections cannot silently change public results. AP Mode remains enabled by default during development. This is not a security boundary yet because the static bundle still contains scouting data.

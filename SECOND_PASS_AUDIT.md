# Slot Map v12.8 — Second-Pass Geocoding Audit

Second-pass artifact reviewed against the v12.7.1 audited production baseline.

## Result
- Newly accepted by Census second pass: 10
- Promoted to production: 4
- Quarantined: 6
- Production mapped establishments: 6,611
- Remaining enrichment queue: 2,819

## Promoted exact matches
- 221001319 — 805 S. Hemlock St., Le Roy, IL 61752
- 220701422 — 1341 S. Washington St., Du Quoin, IL 62832
- 130703069 — 509 North West St., Le Roy, IL 61752
- 170703893 — 106 N. Chestnut Street, Le Roy, IL 61752

These four exact matches do not collide with any existing production coordinate.

## Quarantined Census collisions
The Census geocoder returned identical coordinates for different street numbers in each pair, so these six remain unmapped pending independent verification:
- 120700313 — 121 W. Stevenson Road, Ottawa
- 170701655 — 375 W. Stevenson Rd., Ottawa
- 140703900 — 106 S State St, Marengo
- 180701868 — 100 S State St, Marengo
- 160701588 — 1826 W Reynolds St, Pontiac
- 221002339 — 1910 W Reynolds St, Pontiac

## Quality policy
No non-exact Census matches were promoted. No out-of-Illinois coordinates were accepted. Suspicious coordinate collisions were not allowed into the live map.

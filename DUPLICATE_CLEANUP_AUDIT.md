# Statewide Duplicate / City Normalization Audit

- Master establishments: **9,437**
- Live mapped establishments after quarantine: **6,607**
- Raw unique city strings before cleanup: **1,610**
- Canonical unique city strings after cleanup: **1,069**
- Establishment rows whose city spelling/casing was normalized: **1,732**
- Duplicate license IDs: **0**
- Duplicate normalized name + address + city groups: **0**
- Same-address/different-license groups retained as legitimate: **3**
- Suspicious Census coordinate records quarantined: **6**

## Canonical city aliases fixed

- `dekalb` → **DeKalb**
- `desoto` → **De Soto**
- `downersgrove` → **Downers Grove**
- `duquoin` → **Du Quoin**
- `lasalle` → **LaSalle**
- `leroy` → **Le Roy**
- `mchenry` → **McHenry**
- `mcleansboro` → **McLeansboro**
- `mountprospect` → **Mount Prospect**
- `saintanne` → **St. Anne**
- `saintaugustine` → **St. Augustine**
- `saintcharles` → **St. Charles**

## Same-address groups retained

- **1999 W. 75TH STREET — Woodridge**
  - 150702265 — CORNER CLUBHOUSE BAR AND GRILL, INC.
  - 150702266 — EN GAR INC.
- **1006 East Lincoln St. — Bloomington**
  - 120701356 — David G Dearth
  - 120902173 — John H. Kraus Post No. 454 Veterans of Foreign Wars of the United States
- **1099 S. Water St. — Wilmington**
  - 120700713 — Tuffy's Lounge, Inc.
  - 180701949 — WEE-SIP LIQUORS, INC.

## Quarantined Census collisions

- 140703900 — NGK MARENGO INC. — 106 S State St, Marengo (was 42.2501274, -88.6085909)
- 180701868 — REG VENTURES, INC. — 100 S State St, Marengo (was 42.2501274, -88.6085909)
- 170701655 — Rosati's Pizza Pub Development - Ottawa, LLC — 375 W. Stevenson Rd., Ottawa (was 41.3793433, -88.8417194)
- 221002339 — RR PONTIAC SOUTH LLC — 1910 W REYNOLDS ST, Pontiac (was 40.8736124, -88.6409253)
- 120700313 — Shaker's Lounge, Inc. — 121 W. Stevenson Road, Ottawa (was 41.3793433, -88.8417194)
- 160701588 — Silver Oaks South Inc. — 1826 W Reynolds St, Pontiac (was 40.8736124, -88.6409253)

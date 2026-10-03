# Business Hours / Open Now

Version 13.5.0 adds an `Open Now` filter and per-establishment status support.

Hours are stored on an establishment as `hours` with keys `sun` through `sat`; each value is a list of local America/Chicago intervals such as `10:00-01:00`. Overnight intervals are supported. `hours_source` and `hours_verified` record provenance and freshness.

**Important:** there is no complete official IGB business-hours feed. Locations without independently verified hours remain `Hours unknown` and are excluded when `Open Now` is enabled rather than being guessed closed/open. Statewide hours enrichment therefore remains an ongoing data task.

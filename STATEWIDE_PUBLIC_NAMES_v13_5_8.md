# Statewide public-facing names — v13.5.8

This build applies the Illinois Gaming Board licensee file's official `dba` (doing-business-as) name statewide. This is the closest authoritative statewide field to the name a driver should see on the storefront/sign.

Rules:
- Existing field-/municipal-/official-site verified public names are preserved and take precedence.
- Otherwise, the IGB DBA becomes the primary app display name.
- The prior revenue/legal entity name is retained as `legal_name` and remains visible in establishment details.
- `igb_dba` is retained for audit/search.
- Search indexes display name, IGB DBA, legal name, address, city, ZIP, license and county.
- Records with no official DBA match are left unchanged rather than guessed.

The source `igb-licensee-addresses.json` contains 9,200 statewide license records with DBA values.

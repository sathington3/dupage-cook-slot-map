# Map navigation stability fix — v13.5.1

Fixed a mobile navigation issue where the Leaflet/MarkerCluster map could become glitchy after opening a marker popup, switching to the Establishments page, and then returning to Map.

Changes:
- Stop active map/cluster animations before hiding the map container.
- Close an open popup before switching to Establishments or Filters.
- Clear pending viewport render state before the map is hidden.
- Re-invalidate Leaflet dimensions after the map is visible again using two animation frames plus a follow-up invalidation.
- Avoid unnecessary automatic map fitting when simply returning from Establishments.
- Bump the service-worker cache to v13.5.1 so phones do not keep the older navigation code.

# Target location — geocoded

Confirmed via OpenStreetMap Nominatim (do not hardcode different coordinates without re-checking this).

## Township

**Bandar Serenia / Serenia City**, Kampung Ampar Tenang, Dengkil, Sepang, Selangor, 43900, Malaysia
Township bbox (OSM relation 14186975): lat 2.8415–2.8615, lon 101.6946–101.7117
Township centroid: 2.8454083, 101.7045552

## Chosen precinct

**Serenia Anisa** neighbourhood, rows **Jalan Aman Serenia 17/9** and **Jalan Aman Serenia 17/8**.

- 17/9: single terrace row, units numbered 1–25 (odd), 13 units. Fronts directly onto the
  **Persiaran Bandar Serenia** roundabout (dual-carriageway distributor road) ~20–40m to the north —
  highest noise/sun exposure in the precinct.
  Row reference point: 2.8446264, 101.7029076
- 17/8: parallel terrace row one block south, same orientation, quieter (shielded by the 17/9 row
  and more setback from the main road).
  Row reference point: 2.8441020, 101.7035739

Combined the two rows give ~20+ units with a visible noise/sun gradient from "on the roundabout" to
"one row back" — this is the contrast the demo script (handoff doc §10) needs.

**Precinct bounding box** (for `fetch_osm.py` Overpass queries and DEM/imagery crop):
```
lat_min = 2.8436
lat_max = 2.8450
lon_min = 101.7015
lon_max = 101.7042
```

## Next step

Trace ~20 unit footprints over satellite imagery in geojson.io within the bbox above (prioritise
17/9's 13 units in full, fill the rest from 17/8), assign `front_orientation_deg` from the visible
row direction and `height_m`/`levels` by eye, write to `data/precinct.geojson` per the schema in
CLAUDE.md.

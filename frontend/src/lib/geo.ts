// Mirrors pipeline/config.py's PRECINCT_ORIGIN_LONLAT / local East-North-Up projection,
// so a unit's footprint lines up the same way in the browser as it does in the pipeline's
// raycasting scene.
export const PRECINCT_ORIGIN_LONLAT: [number, number] = [101.70285, 2.8443];

const M_PER_DEG_LAT = 111_320;

function mPerDegLon(latDeg: number) {
  return 111_320 * Math.cos((latDeg * Math.PI) / 180);
}

/** lon/lat (deg) -> local {x: east_m, z: north_m}, three.js Y-up frame. */
export function project(lon: number, lat: number): { x: number; z: number } {
  const [originLon, originLat] = PRECINCT_ORIGIN_LONLAT;
  return {
    x: (lon - originLon) * mPerDegLon(originLat),
    z: (lat - originLat) * M_PER_DEG_LAT,
  };
}

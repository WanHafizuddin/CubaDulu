const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type Polygon = { type: "Polygon"; coordinates: number[][][] };

export type UnitRecord = {
  unit_id: string;
  unit_type: string;
  levels: number;
  height_m: number;
  front_orientation_deg: number;
  price_rm: number;
  row: string;
  geometry: Polygon;
  sun: {
    facade_sun_hours: Record<string, number>;
    roof_sun_hours: number;
    afternoon_sun_hours_after_2pm: number;
    heat_rating: string;
    hourly_sunlit: Record<string, string[]>;
    indicative: boolean;
  };
};

export async function fetchUnits(): Promise<UnitRecord[]> {
  const res = await fetch(`${API_BASE_URL}/units`);
  if (!res.ok) throw new Error(`GET /units failed: ${res.status}`);
  return res.json();
}

export async function fetchUnit(unitId: string): Promise<UnitRecord> {
  const res = await fetch(`${API_BASE_URL}/units/${unitId}`);
  if (!res.ok) throw new Error(`GET /units/${unitId} failed: ${res.status}`);
  return res.json();
}

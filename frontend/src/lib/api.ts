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
  noise: {
    hourly_db: Record<string, number>;
    rating: string;
    dominant_source: string | null;
    indicative: boolean;
  };
  commute: {
    destinations: Record<string, { am_min: number; pm_min: number }>;
  };
  amenities: Record<string, { name: string | null; walk_min: number }>;
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

export type MatchResult = {
  weights: Record<string, unknown>;
  results: { unit_id: string; explanation: string }[];
};

async function parseJsonOrThrow(res: Response, label: string) {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `${label} failed: ${res.status}`);
  }
  return res.json();
}

export async function matchUnits(description: string): Promise<MatchResult> {
  const res = await fetch(`${API_BASE_URL}/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description }),
  });
  return parseJsonOrThrow(res, "POST /match");
}

export type ChatMessage = { role: "user" | "assistant"; content: string };

export async function chatWithUnit(
  unitId: string,
  message: string,
  history: ChatMessage[],
): Promise<{ answer: string }> {
  const res = await fetch(`${API_BASE_URL}/units/${unitId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });
  return parseJsonOrThrow(res, `POST /units/${unitId}/chat`);
}

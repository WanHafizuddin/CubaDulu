import { useEffect, useState } from "react";
import { fetchUnit, type UnitRecord } from "../lib/api";

const HEAT_STYLES: Record<string, string> = {
  Low: "bg-green-100 text-green-800",
  Moderate: "bg-yellow-100 text-yellow-800",
  High: "bg-red-100 text-red-800",
};

function ComingSoon({ label }: { label: string }) {
  return (
    <div className="flex items-center justify-between text-sm text-gray-400">
      <span>{label}</span>
      <span className="italic">not modelled yet</span>
    </div>
  );
}

export default function LivabilityCard({ unitId }: { unitId: string }) {
  const [unit, setUnit] = useState<UnitRecord | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setUnit(null);
    setError(null);
    fetchUnit(unitId)
      .then(setUnit)
      .catch((err) => setError(String(err)));
  }, [unitId]);

  if (error) return <div className="border rounded p-4 text-red-600 text-sm">{error}</div>;
  if (!unit) return <div className="border rounded p-4 text-sm text-gray-400">Loading…</div>;

  const { sun } = unit;
  const facades = ["N", "E", "S", "W"] as const;

  return (
    <div className="border rounded p-4 flex flex-col gap-3">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="font-semibold text-lg">{unit.unit_id}</h2>
          <p className="text-sm text-gray-500">
            {unit.unit_type} · {unit.levels}-storey · {unit.row}
          </p>
        </div>
        <p className="font-semibold">RM {unit.price_rm.toLocaleString()}</p>
      </div>

      <div>
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Sun &amp; heat</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${HEAT_STYLES[sun.heat_rating] ?? "bg-gray-100 text-gray-600"}`}>
            {sun.heat_rating}
          </span>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {sun.afternoon_sun_hours_after_2pm}h of direct west sun after 2pm · indicative estimate
        </p>
        <div className="grid grid-cols-4 gap-2 mt-2 text-center">
          {facades.map((f) => (
            <div key={f} className="bg-gray-50 rounded py-1">
              <div className="text-xs text-gray-400">{f}</div>
              <div className="text-sm font-medium">{sun.facade_sun_hours[f] ?? 0}h</div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-1 pt-2 border-t">
        <ComingSoon label="Noise" />
        <ComingSoon label="Commute" />
        <ComingSoon label="Flood" />
        <ComingSoon label="Amenities" />
      </div>
    </div>
  );
}

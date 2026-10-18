import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import LivabilityCard from "../components/LivabilityCard";
import { fetchUnits, type UnitRecord } from "../lib/api";

const HEAT_RANK: Record<string, number> = { Low: 0, Moderate: 1, High: 2 };

function UnitPicker({
  label,
  units,
  value,
  onChange,
}: {
  label: string;
  units: UnitRecord[];
  value: string;
  onChange: (unitId: string) => void;
}) {
  return (
    <label className="flex items-center gap-2 text-sm">
      <span className="text-gray-500">{label}</span>
      <select className="border rounded px-2 py-1" value={value} onChange={(e) => onChange(e.target.value)}>
        {units.map((u) => (
          <option key={u.unit_id} value={u.unit_id}>
            {u.unit_id} · RM {u.price_rm.toLocaleString()}
          </option>
        ))}
      </select>
    </label>
  );
}

function Delta({ unitA, unitB }: { unitA: UnitRecord; unitB: UnitRecord }) {
  const priceDiff = unitA.price_rm - unitB.price_rm;
  const heatDiff = HEAT_RANK[unitA.sun.heat_rating] - HEAT_RANK[unitB.sun.heat_rating];

  return (
    <div className="border rounded p-3 text-sm flex flex-col gap-1 bg-gray-50">
      {priceDiff !== 0 && (
        <p>
          <strong>{priceDiff < 0 ? unitA.unit_id : unitB.unit_id}</strong> is RM {Math.abs(priceDiff).toLocaleString()} cheaper.
        </p>
      )}
      {heatDiff !== 0 && (
        <p>
          <strong>{heatDiff < 0 ? unitA.unit_id : unitB.unit_id}</strong> runs cooler ({heatDiff < 0 ? unitA.sun.heat_rating : unitB.sun.heat_rating} vs {heatDiff < 0 ? unitB.sun.heat_rating : unitA.sun.heat_rating}).
        </p>
      )}
      {priceDiff === 0 && heatDiff === 0 && <p>Same price and heat rating.</p>}
    </div>
  );
}

export default function ComparePage() {
  const [params, setParams] = useSearchParams();
  const [units, setUnits] = useState<UnitRecord[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUnits()
      .then(setUnits)
      .catch((err) => setError(String(err)));
  }, []);

  const ids = (params.get("ids") ?? "").split(",").filter(Boolean);
  const idA = ids[0] ?? units[0]?.unit_id ?? "";
  const idB = ids[1] ?? units[1]?.unit_id ?? "";

  function setIds(a: string, b: string) {
    setParams({ ids: `${a},${b}` });
  }

  if (error) return <div className="p-4 text-red-600 text-sm">{error}</div>;
  if (units.length < 2) return <div className="p-4 text-sm text-gray-400">Loading…</div>;

  const unitA = units.find((u) => u.unit_id === idA);
  const unitB = units.find((u) => u.unit_id === idB);

  return (
    <div className="p-4 flex flex-col gap-4">
      <div className="flex gap-6 flex-wrap">
        <UnitPicker label="Unit A" units={units} value={idA} onChange={(id) => setIds(id, idB)} />
        <UnitPicker label="Unit B" units={units} value={idB} onChange={(id) => setIds(idA, id)} />
      </div>

      {unitA && unitB && <Delta unitA={unitA} unitB={unitB} />}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {idA && <LivabilityCard unitId={idA} />}
        {idB && <LivabilityCard unitId={idB} />}
      </div>
    </div>
  );
}

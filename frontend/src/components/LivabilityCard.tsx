// Sun/heat, noise, commute, flood, amenities summary for one unit. GET /units/{unitId}.
export default function LivabilityCard({ unitId }: { unitId: string }) {
  // TODO: fetch unit record, render factor badges; label modelled values "indicative"
  return <div className="border rounded p-4">Livability card: {unitId}</div>;
}

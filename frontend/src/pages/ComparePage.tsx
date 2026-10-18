import { useSearchParams } from "react-router-dom";
import LivabilityCard from "../components/LivabilityCard";

export default function ComparePage() {
  const [params] = useSearchParams();
  const ids = (params.get("ids") ?? "").split(",").filter(Boolean);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
      {ids.map((id) => (
        <LivabilityCard key={id} unitId={id} />
      ))}
    </div>
  );
}

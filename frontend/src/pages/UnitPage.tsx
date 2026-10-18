import { useState } from "react";
import { useParams } from "react-router-dom";
import ChatPanel from "../components/ChatPanel";
import LivabilityCard from "../components/LivabilityCard";
import TimeSlider from "../components/TimeSlider";
import UnitScene3D from "../components/UnitScene3D";

export default function UnitPage() {
  const { unitId } = useParams();
  const [hour, setHour] = useState(15);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
      <div>
        <UnitScene3D unitId={unitId!} hour={hour} />
        <TimeSlider hour={hour} onChange={setHour} />
      </div>
      <div className="flex flex-col gap-4">
        <LivabilityCard unitId={unitId!} />
        <ChatPanel unitId={unitId!} />
      </div>
    </div>
  );
}

import { useState } from "react";

export default function TimeSlider() {
  const [hour, setHour] = useState(12);

  return (
    <div className="mt-2">
      <input
        type="range"
        min={7}
        max={19}
        value={hour}
        onChange={(e) => setHour(Number(e.target.value))}
        className="w-full"
      />
      <div className="text-sm text-gray-500">{hour}:00</div>
    </div>
  );
}

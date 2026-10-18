export default function TimeSlider({ hour, onChange }: { hour: number; onChange: (hour: number) => void }) {
  return (
    <div className="mt-2">
      <input
        type="range"
        min={7}
        max={19}
        value={hour}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full"
      />
      <div className="text-sm text-gray-500">{hour}:00</div>
    </div>
  );
}

// three.js close-up of a single unit, shadows driven by SunCalc sun position.
export default function UnitScene3D({ unitId }: { unitId: string }) {
  // TODO: three.js scene, extruded unit mesh, directional light positioned via SunCalc
  // for the selected time, synced to TimeSlider state
  return <div className="h-96 bg-gray-200 flex items-center justify-center">3D view: {unitId}</div>;
}

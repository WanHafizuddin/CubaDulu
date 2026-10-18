import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchUnits, type Polygon, type UnitRecord } from "../lib/api";
import { PRECINCT_ORIGIN_LONLAT } from "../lib/geo";

type Factor = "heat" | "noise" | "flood";

const FACTORS: { id: Factor; label: string; available: boolean }[] = [
  { id: "heat", label: "Heat", available: true },
  { id: "noise", label: "Noise", available: false },
  { id: "flood", label: "Flood", available: false },
];

const HEAT_COLORS: Record<string, string> = {
  Low: "#4ade80",
  Moderate: "#facc15",
  High: "#f87171",
};

type UnitFeatureCollection = {
  type: "FeatureCollection";
  features: { type: "Feature"; properties: Record<string, unknown>; geometry: Polygon }[];
};

function unitsToGeoJSON(units: UnitRecord[]): UnitFeatureCollection {
  return {
    type: "FeatureCollection",
    features: units.map((u) => ({
      type: "Feature",
      properties: {
        unit_id: u.unit_id,
        height_m: u.height_m,
        heat_rating: u.sun.heat_rating,
        heat_color: HEAT_COLORS[u.sun.heat_rating] ?? "#9ca3af",
        price_rm: u.price_rm,
      },
      geometry: u.geometry,
    })),
  };
}

export default function PrecinctMap() {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [factor, setFactor] = useState<Factor>("heat");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const map = new maplibregl.Map({
      container,
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: "© OpenStreetMap contributors",
          },
        },
        layers: [{ id: "osm", type: "raster", source: "osm" }],
      },
      center: PRECINCT_ORIGIN_LONLAT,
      zoom: 18,
      pitch: 45,
      bearing: 0,
      canvasContextAttributes: { antialias: true },
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl(), "top-right");

    map.on("load", () => {
      fetchUnits()
        .then((units) => {
          map.addSource("units", { type: "geojson", data: unitsToGeoJSON(units) });
          map.addLayer({
            id: "units-extrusion",
            type: "fill-extrusion",
            source: "units",
            paint: {
              "fill-extrusion-color": ["get", "heat_color"],
              "fill-extrusion-height": ["get", "height_m"],
              "fill-extrusion-opacity": 0.9,
            },
          });

          const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });
          map.on("mousemove", "units-extrusion", (e) => {
            map.getCanvas().style.cursor = "pointer";
            const f = e.features?.[0];
            if (!f) return;
            popup
              .setLngLat(e.lngLat)
              .setHTML(`<strong>${f.properties!.unit_id}</strong><br/>Heat: ${f.properties!.heat_rating}<br/>RM ${f.properties!.price_rm}`)
              .addTo(map);
          });
          map.on("mouseleave", "units-extrusion", () => {
            map.getCanvas().style.cursor = "";
            popup.remove();
          });
          map.on("click", "units-extrusion", (e) => {
            const unitId = e.features?.[0]?.properties?.unit_id;
            if (unitId) navigate(`/units/${unitId}`);
          });
        })
        .catch((err) => setError(String(err)));
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  return (
    <div className="relative h-full w-full">
      <div ref={containerRef} className="h-full w-full" />
      <div className="absolute top-2 left-2 bg-white rounded shadow px-2 py-1 flex gap-1 text-sm">
        {FACTORS.map((f) => (
          <button
            key={f.id}
            type="button"
            disabled={!f.available}
            onClick={() => setFactor(f.id)}
            title={f.available ? undefined : "Coming soon"}
            className={[
              "px-2 py-1 rounded",
              factor === f.id ? "bg-black text-white" : "bg-gray-100",
              !f.available && "opacity-40 cursor-not-allowed",
            ].join(" ")}
          >
            {f.label}
          </button>
        ))}
      </div>
      {error && <div className="absolute top-2 right-2 text-sm text-red-600 bg-white/80 px-2 py-1 rounded">{error}</div>}
    </div>
  );
}

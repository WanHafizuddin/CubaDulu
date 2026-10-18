import * as SunCalc from "suncalc";
import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { type UnitRecord, fetchUnits } from "../lib/api";
import { project } from "../lib/geo";

// Representative date for the shadow demo — mirrors pipeline/config.py's
// SUN_REFERENCE_DATES["equinox"]. Kuala Lumpur has no DST, fixed UTC+8.
const SUN_REFERENCE_DATE = "2026-03-20";
const KL_UTC_OFFSET_HOURS = 8;

function sunDirectionForHour(hour: number, lat: number, lon: number) {
  const [y, m, d] = SUN_REFERENCE_DATE.split("-").map(Number);
  const when = new Date(Date.UTC(y, m - 1, d, hour - KL_UTC_OFFSET_HOURS));
  const { azimuth, altitude } = SunCalc.getPosition(when, lat, lon);
  // SunCalc azimuth: radians, measured from south, clockwise toward west.
  // Compass bearing (from north, clockwise) = azimuth + PI.
  const bearing = azimuth + Math.PI;
  const east = Math.cos(altitude) * Math.sin(bearing);
  const north = Math.cos(altitude) * Math.cos(bearing);
  const up = Math.sin(altitude);
  return { x: east, y: up, z: -north, altitude };
}

function buildingMesh(unit: UnitRecord, highlighted: boolean) {
  const ring = unit.geometry.coordinates[0];
  const pts = ring
    .slice(0, -1)
    .map(([lon, lat]) => project(lon, lat))
    .map((p) => new THREE.Vector2(p.x, p.z));
  const shape = new THREE.Shape(pts);
  const geometry = new THREE.ExtrudeGeometry(shape, { depth: unit.height_m, bevelEnabled: false });
  geometry.rotateX(-Math.PI / 2);
  const material = new THREE.MeshStandardMaterial({
    color: highlighted ? 0xf2a65a : 0xd8d2c4,
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

export default function UnitScene3D({ unitId, hour }: { unitId: string; hour: number }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const lightRef = useRef<THREE.DirectionalLight | null>(null);
  const targetLonLatRef = useRef<[number, number]>([101.70285, 2.8443]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let frameId: number;
    const container = containerRef.current;
    if (!container) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xbfd7ea);

    const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    container.appendChild(renderer.domElement);

    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(300, 300),
      new THREE.MeshStandardMaterial({ color: 0x8fb28f }),
    );
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    scene.add(new THREE.AmbientLight(0xffffff, 0.6));

    const light = new THREE.DirectionalLight(0xffffff, 1.5);
    light.castShadow = true;
    light.shadow.mapSize.set(1024, 1024);
    light.shadow.camera.left = -60;
    light.shadow.camera.right = 60;
    light.shadow.camera.top = 60;
    light.shadow.camera.bottom = -60;
    light.shadow.camera.near = 1;
    light.shadow.camera.far = 300;
    scene.add(light);
    scene.add(light.target);
    lightRef.current = light;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    function resize() {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight || 384;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }

    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(container);
    resize();

    function animate() {
      frameId = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    fetchUnits()
      .then((units) => {
        if (cancelled) return;
        const target = units.find((u) => u.unit_id === unitId);
        if (!target) {
          setError(`Unit ${unitId} not found`);
          return;
        }
        const ring = target.geometry.coordinates[0].slice(0, -1);
        const centroidLon = ring.reduce((s, c) => s + c[0], 0) / ring.length;
        const centroidLat = ring.reduce((s, c) => s + c[1], 0) / ring.length;
        targetLonLatRef.current = [centroidLon, centroidLat];
        const targetXZ = project(centroidLon, centroidLat);

        for (const unit of units) {
          scene.add(buildingMesh(unit, unit.unit_id === unitId));
        }

        camera.position.set(targetXZ.x + 25, 22, targetXZ.z + 25);
        controls.target.set(targetXZ.x, target.height_m / 2, targetXZ.z);
        light.target.position.set(targetXZ.x, 0, targetXZ.z);
        controls.update();

        const dir = sunDirectionForHour(hour, centroidLat, centroidLon);
        light.position.set(targetXZ.x + dir.x * 60, Math.max(dir.y, 0.05) * 60, targetXZ.z + dir.z * 60);
        light.intensity = dir.altitude > 0 ? 1.5 : 0.1;
      })
      .catch((err) => setError(String(err)));

    return () => {
      cancelled = true;
      cancelAnimationFrame(frameId);
      resizeObserver.disconnect();
      controls.dispose();
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  }, [unitId]);

  useEffect(() => {
    const light = lightRef.current;
    if (!light) return;
    const [lon, lat] = targetLonLatRef.current;
    const dir = sunDirectionForHour(hour, lat, lon);
    const target = light.target.position;
    light.position.set(target.x + dir.x * 60, Math.max(dir.y, 0.05) * 60, target.z + dir.z * 60);
    light.intensity = dir.altitude > 0 ? 1.5 : 0.1;
  }, [hour]);

  return (
    <div className="relative">
      <div ref={containerRef} className="h-96 w-full" />
      {error && <div className="absolute top-2 left-2 text-sm text-red-600 bg-white/80 px-2 py-1 rounded">{error}</div>}
    </div>
  );
}

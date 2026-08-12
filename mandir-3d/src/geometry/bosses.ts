/** The boss courses (doc §2.4) — the ONE exterior ornament family at
 * three scales: beam Ø90@180 (band face) · kaṇṭha Ø60@120 (podium
 * recess) · cornice Ø50@110 (under the corona). Studs in registers,
 * centered-residual closure (pitches NEVER stretch), quiet corners.
 *
 * One InstancedMesh per course × facade (12 draws). Small bosses do NOT
 * cast shadows (1–3 texels in a 2048 map would shimmer); they receive.
 * Relief: rise 0.42·r on a 1.15·Ø plate; the beam course adds a 0.55·r
 * shoulder.
 */
import * as THREE from "three/webgpu";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import type { MaterialLib } from "../materials/materials";
import {
  bandSpec,
  bodyDepth,
  bossFamily,
  envelopes,
  podiumProfile,
  porchProjection,
} from "./dimensions";
import type { BuiltPart } from "./podium";

/** dome cap + plate, axis +z (projecting from a wall face) */
function bossGeometry(d: number, withShoulder: boolean): THREE.BufferGeometry {
  const r = d / 2;
  const rise = bossFamily.riseFactor * r;
  const plateR = (bossFamily.plateFactor * d) / 2;
  const parts: THREE.BufferGeometry[] = [];

  const plate = new THREE.CylinderGeometry(plateR, plateR, 0.01, 20);
  plate.rotateX(Math.PI / 2);
  plate.translate(0, 0, 0.005);
  parts.push(plate);

  if (withShoulder) {
    const shR = r + bossFamily.beamShoulderFactor * r * 0.5;
    const sh = new THREE.CylinderGeometry(shR, shR, 0.008, 20);
    sh.rotateX(Math.PI / 2);
    sh.translate(0, 0, 0.014);
    parts.push(sh);
  }

  // spherical cap: sphere radius R from cap radius r and rise h:
  // R = (r² + h²) / 2h; cut angle θ = acos(1 − h/R)
  const R = (r * r + rise * rise) / (2 * rise);
  const theta = Math.acos(1 - rise / R);
  const cap = new THREE.SphereGeometry(R, 18, 8, 0, Math.PI * 2, 0, theta);
  cap.rotateX(Math.PI / 2);
  const zBase = withShoulder ? 0.018 : 0.01;
  cap.translate(0, 0, zBase + rise - R);
  parts.push(cap);

  const merged = mergeGeometries(parts)!;
  parts.forEach((g) => g.dispose());
  return merged;
}

interface CourseSpec {
  name: string;
  d: number;
  pitch: number;
  /** face rectangle the course wraps (w × depth) and its face offset */
  rectW: number;
  rectD: number;
  faceOffset: number;
  y: number;
  /** the rect's center z in MODEL frame (podium 0, body offset) */
  centerZ: number;
  withShoulder: boolean;
}

export function buildBosses(lib: MaterialLib): BuiltPart {
  const group = new THREE.Group();
  group.name = "boss-courses";

  const sW = envelopes.structuralW.v;
  const bD = bodyDepth.v;
  const podW = envelopes.podiumW.v;
  const podD = envelopes.podiumD.v;
  // body center in MODEL frame (the same closure the walls use)
  const bodyCenterZ = podD / 2 - envelopes.walk.v - porchProjection.v - bD / 2;

  const courses: CourseSpec[] = [
    {
      name: "beam",
      d: bossFamily.beam.d.v,
      pitch: bossFamily.beam.pitch.v,
      rectW: sW,
      rectD: bD,
      faceOffset: bandSpec.beamProud.v,
      y: bandSpec.beamBossCenterY.v,
      centerZ: bodyCenterZ,
      withShoulder: true,
    },
    {
      name: "kantha",
      d: bossFamily.kantha.d.v,
      pitch: bossFamily.kantha.pitch.v,
      rectW: podW,
      rectD: podD,
      faceOffset: -podiumProfile.kanthaRecess.v, // protected IN the recess
      y: bandSpec.kanthaBossCenterY.v,
      centerZ: 0,
      withShoulder: false,
    },
    {
      name: "cornice",
      d: bossFamily.cornice.d.v,
      pitch: bossFamily.cornice.pitch.v,
      rectW: sW,
      rectD: bD,
      faceOffset: bandSpec.corniceFasciaProud.v,
      y: bandSpec.corniceBossCenterY.v,
      centerZ: bodyCenterZ,
      withShoulder: false,
    },
  ];

  const SYSTEM = [12, 24];
  const facades: { name: string; angle: number }[] = [
    { name: "front", angle: 0 },
    { name: "right", angle: Math.PI / 2 },
    { name: "rear", angle: Math.PI },
    { name: "left", angle: -Math.PI / 2 },
  ];

  for (const c of courses) {
    const geo = bossGeometry(c.d, c.withShoulder);
    for (const f of facades) {
      const faceLen = f.name === "front" || f.name === "rear" ? c.rectW : c.rectD;
      const planeDist =
        (f.name === "front" || f.name === "rear" ? c.rectD : c.rectW) / 2 + c.faceOffset;
      const usable = faceLen - 2 * bandSpec.bossRunMargin.v;
      const count = Math.max(2, Math.floor(usable / c.pitch) + 1);
      if (SYSTEM.includes(count)) {
        // law 3: never a system number on a repeating run — drop one
        throw new Error(`boss run ${c.name}/${f.name} would count ${count}`);
      }
      const rowLen = (count - 1) * c.pitch;
      const inst = new THREE.InstancedMesh(geo, lib.sandstone, count);
      inst.name = `bosses-${c.name}-${f.name}`;
      inst.castShadow = false; // shadow policy: small courses never cast
      inst.receiveShadow = true;
      const m = new THREE.Matrix4();
      const rot = new THREE.Matrix4().makeRotationY(f.angle);
      const pos = new THREE.Vector3();
      for (let i = 0; i < count; i++) {
        const u = -rowLen / 2 + i * c.pitch;
        // local (u, y, planeDist) rotated to the facade + rect center
        pos.set(u, c.y, planeDist).applyMatrix4(rot);
        pos.z += c.centerZ;
        m.copy(rot).setPosition(pos);
        inst.setMatrixAt(i, m);
      }
      inst.instanceMatrix.needsUpdate = true;
      inst.computeBoundingBox();
      inst.computeBoundingSphere();
      group.add(inst);
    }
  }

  return { group, anchors: {} };
}

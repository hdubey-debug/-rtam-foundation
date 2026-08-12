/** Named-group measurements in REAL METERS — the codex/measures.json eyes.
 * Box3 checks bind to NAMED parts against NAMED envelopes; the raw model
 * bounds (stair run, dhvaja pole) are reported but never asserted.
 */
import * as THREE from "three/webgpu";
import { bodyDepth, envelopes, stations, FT } from "../geometry/dimensions";

export interface GroupMeasure {
  size: number[];
  min: number[];
  max: number[];
}

export interface Measures {
  groups: Record<string, GroupMeasure>;
  anchorsY: Record<string, number>;
  checks: { name: string; ok: boolean; got: number; want: number; tolM: number }[];
}

const MEASURED = ["podium", "body", "main-roof", "tower-shaft", "kalasha", "verandah-roof"];

export function measureModel(real: THREE.Object3D, anchors?: Record<string, THREE.Vector3>): Measures {
  real.updateWorldMatrix(true, true);
  const inv = real.matrixWorld.clone().invert();
  const groups: Record<string, GroupMeasure> = {};

  for (const name of MEASURED) {
    const obj = real.getObjectByName(name);
    if (!obj) continue;
    const box = new THREE.Box3().setFromObject(obj);
    // express in the model's own frame (real meters)
    box.applyMatrix4(inv);
    const size = box.getSize(new THREE.Vector3());
    groups[name] = {
      size: [size.x, size.y, size.z],
      min: box.min.toArray(),
      max: box.max.toArray(),
    };
  }

  const anchorsY: Record<string, number> = {};
  for (const [k, v] of Object.entries(anchors ?? {})) anchorsY[k] = v.y;

  const TOL = 0.01; // the DoD's ±1 cm
  const checks: Measures["checks"] = [];
  const check = (name: string, got: number | undefined, want: number) => {
    if (got === undefined) return;
    checks.push({ name, ok: Math.abs(got - want) <= TOL, got, want, tolM: TOL });
  };

  // a missing named group is a FAILURE, not a silently skipped check
  const REQUIRED = ["podium", "body", "main-roof", "tower-shaft", "kalasha"];
  for (const name of REQUIRED) {
    if (!groups[name]) checks.push({ name: `${name} present`, ok: false, got: 0, want: 1, tolM: 0 });
  }

  check("podium.w = 52 ft", groups.podium?.size[0], envelopes.podiumW.v);
  check("podium.d = 88 ft", groups.podium?.size[2], envelopes.podiumD.v);
  check("body.w = structuralW", groups.body?.size[0], envelopes.structuralW.v);
  check("body.d = ten bays", groups.body?.size[2], bodyDepth.v);
  check("body top = plate 30 ft", groups.body?.max[1], stations.plateY.v);
  // the GEOMETRY hits the tip datum, not just the anchor metadata
  check("kalasha GEOMETRY maxY = 52 ft", groups.kalasha?.max[1], stations.kalashaTipY.v);
  check("kalasha-tip anchor = 52 ft", anchorsY["kalasha-tip"], 52 * FT);
  check("roof ridge datum", groups["main-roof"]?.max[1], stations.mainRidgeY.v);

  // roofs stay INSIDE the podium envelope; `got` reports the WORST
  // signed excess across all four plan bounds (x and z)
  const podHalfW = envelopes.podiumW.v / 2;
  const podHalfD = envelopes.podiumD.v / 2;
  const inside = (name: string, g?: GroupMeasure) => {
    if (!g) return;
    const excess = Math.max(
      g.max[0] - podHalfW,
      -podHalfW - g.min[0],
      g.max[2] - podHalfD,
      -podHalfD - g.min[2],
    );
    checks.push({ name: `${name} inside podium envelope`, ok: excess <= TOL, got: excess, want: 0, tolM: TOL });
  };
  inside("main-roof", groups["main-roof"]);
  inside("verandah-roof", groups["verandah-roof"]);

  return { groups, anchorsY, checks };
}
